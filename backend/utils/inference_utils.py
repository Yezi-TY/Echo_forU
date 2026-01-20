"""
推理工具函数 - 封装 inference.py 中的逻辑
"""
import os
import re
import json
import random
import numpy as np
import torch
import torchaudio
import pedalboard
from pathlib import Path
from typing import Optional, Tuple, Callable
from huggingface_hub import hf_hub_download

from muq import MuQMuLan
from backend.diffrhythm2.cfm import CFM
from backend.diffrhythm2.backbones.dit import DiT
from backend.bigvgan.model import Generator

# 结构标记信息
STRUCT_INFO = {
    "[start]": 500,
    "[end]": 501,
    "[intro]": 502,
    "[verse]": 503,
    "[chorus]": 504,
    "[outro]": 505,
    "[inst]": 506,
    "[solo]": 507,
    "[bridge]": 508,
    "[hook]": 509,
    "[break]": 510,
    "[stop]": 511,
    "[space]": 512
}

STRUCT_PATTERN = re.compile(r'^\[.*?\]$')


class CNENTokenizer:
    """中英文分词器"""
    def __init__(self, vocab_path: Optional[Path] = None):
        if vocab_path is None:
            # 从项目根目录查找 vocab.json
            project_root = Path(__file__).parent.parent.parent
            vocab_path = project_root / "backend" / "g2p" / "g2p" / "vocab.json"
        
        # Windows 上默认编码可能是 cp936/gbk，vocab.json 含 IPA 字符会解码失败；
        # 这里显式用 UTF-8（兼容 UTF-8 BOM 用 utf-8-sig）
        with open(vocab_path, "r", encoding="utf-8-sig") as file:
            self.phone2id: dict = json.load(file)["vocab"]
        self.id2phone = {v: k for (k, v) in self.phone2id.items()}
        
        from backend.g2p.g2p_generation import chn_eng_g2p
        self.tokenizer = chn_eng_g2p
    
    def encode(self, text):
        phone, token = self.tokenizer(text)
        token = [x + 1 for x in token]
        return token
    
    def decode(self, token):
        return "|".join([self.id2phone[x - 1] for x in token])


def prepare_models(repo_id: str, ckpt_dir: Path, device: torch.device) -> Tuple:
    """准备所有模型（diffrhythm2, mulan, tokenizer, decoder）"""
    import logging
    logger = logging.getLogger(__name__)
    
    # 记录设备信息
    device_str = str(device)
    logger.info(f"[GPU] Preparing models on device: {device_str}")
    if device.type == 'cuda':
        if torch.cuda.is_available():
            logger.info(f"[OK] CUDA available: {torch.cuda.get_device_name(0)}")
            logger.info(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        else:
            logger.warning("[WARN] CUDA device requested but not available, falling back to CPU")
            device = torch.device('cpu')
            device_str = 'cpu'
    
    # 下载并加载 DiffRhythm2 模型
    diffrhythm2_ckpt_path = hf_hub_download(
        repo_id=repo_id,
        filename="model.safetensors",
        local_dir=str(ckpt_dir),
        local_files_only=False,
    )
    diffrhythm2_config_path = hf_hub_download(
        repo_id=repo_id,
        filename="config.json",
        local_dir=str(ckpt_dir),
        local_files_only=False,
    )
    
    with open(diffrhythm2_config_path) as f:
        model_config = json.load(f)
    
    model_config['use_flex_attn'] = False
    diffrhythm2 = CFM(
        transformer=DiT(**model_config),
        num_channels=model_config['mel_dim'],
        block_size=model_config['block_size'],
    )
    
    # 先移动到目标设备，再加载权重（更高效）
    diffrhythm2 = diffrhythm2.to(device)
    logger.info(f"[LOAD] Loading DiffRhythm2 weights to {device_str}...")
    if diffrhythm2_ckpt_path.endswith('.safetensors'):
        from safetensors.torch import load_file
        # safetensors 需要先加载到 CPU，然后移动到设备
        ckpt = load_file(diffrhythm2_ckpt_path)
        # 将权重移动到目标设备
        ckpt = {k: v.to(device) for k, v in ckpt.items()}
    else:
        # 直接加载到目标设备
        ckpt = torch.load(diffrhythm2_ckpt_path, map_location=device)
    diffrhythm2.load_state_dict(ckpt)
    # 验证模型在正确的设备上
    actual_device = next(diffrhythm2.parameters()).device
    logger.info(f"[OK] DiffRhythm2 loaded on {actual_device}")
    if device.type == 'cuda' and actual_device.type != 'cuda':
        logger.warning(f"[WARN] Model is on {actual_device} but expected {device}")
    
    # 加载 Mulan
    logger.info(f"[LOAD] Loading MuQ-MuLan to {device_str}...")
    mulan = MuQMuLan.from_pretrained("OpenMuQ/MuQ-MuLan-large", cache_dir=str(ckpt_dir)).to(device)
    actual_device = next(mulan.parameters()).device
    logger.info(f"[OK] MuQ-MuLan loaded on {actual_device}")
    
    # 加载分词器
    lrc_tokenizer = CNENTokenizer()
    
    # 加载解码器
    logger.info(f"[LOAD] Loading decoder to {device_str}...")
    decoder_ckpt_path = hf_hub_download(
        repo_id=repo_id,
        filename="decoder.bin",
        local_dir=str(ckpt_dir),
        local_files_only=False,
    )
    decoder_config_path = hf_hub_download(
        repo_id=repo_id,
        filename="decoder.json",
        local_dir=str(ckpt_dir),
        local_files_only=False,
    )
    # 创建解码器（权重会先加载到 CPU）
    decoder = Generator(decoder_config_path, decoder_ckpt_path)
    # 移动到目标设备（这会移动所有权重）
    decoder = decoder.to(device)
    # 确保解码器内部模型也在正确的设备上
    if hasattr(decoder, 'decoder'):
        decoder.decoder = decoder.decoder.to(device)
    actual_device = next(decoder.parameters()).device
    logger.info(f"[OK] Decoder loaded on {actual_device}")
    
    # 最终验证所有模型都在正确的设备上
    models = [("DiffRhythm2", diffrhythm2), ("MuQ-MuLan", mulan), ("Decoder", decoder)]
    all_on_correct_device = True
    for name, model in models:
        model_device = next(model.parameters()).device
        if model_device != device:
            logger.warning(f"[WARN] {name} is on {model_device} but expected {device}")
            all_on_correct_device = False
    
    if all_on_correct_device:
        logger.info(f"[OK] All models successfully loaded on {device_str}")
    else:
        logger.warning("[WARN] Some models may not be on the expected device")
    
    return diffrhythm2, mulan, lrc_tokenizer, decoder


def parse_lyrics(lyrics: str, tokenizer: CNENTokenizer) -> list:
    """解析歌词"""
    lyrics_with_time = []
    lyrics_lines = lyrics.split("\n")
    get_start = False
    
    for line in lyrics_lines:
        line = line.strip()
        if not line:
            continue
        struct_flag = STRUCT_PATTERN.match(line)
        if struct_flag:
            struct_idx = STRUCT_INFO.get(line.lower(), None)
            if struct_idx is not None:
                if struct_idx == STRUCT_INFO['[start]']:
                    get_start = True
                lyrics_with_time.append([struct_idx, STRUCT_INFO['[stop]']])
            else:
                continue
        else:
            tokens = tokenizer.encode(line.strip())
            tokens = tokens + [STRUCT_INFO['[stop]']]
            lyrics_with_time.append(tokens)
    
    if len(lyrics_with_time) != 0 and not get_start:
        lyrics_with_time = [[STRUCT_INFO['[start]'], STRUCT_INFO['[stop]']]] + lyrics_with_time
    
    return lyrics_with_time


def make_fake_stereo(audio: np.ndarray, sampling_rate: int) -> np.ndarray:
    """创建伪立体声"""
    left_channel = audio
    right_channel = audio.copy()
    right_channel = right_channel * 0.8
    delay_samples = int(0.01 * sampling_rate)
    right_channel = np.roll(right_channel, delay_samples)
    right_channel[:, :delay_samples] = 0
    stereo_audio = np.concatenate([left_channel, right_channel], axis=0)
    return stereo_audio


def run_inference(
    model: CFM,
    decoder: Generator,
    text: torch.Tensor,
    style_prompt: torch.Tensor,
    duration: float,
    output_path: Path,
    cfg_strength: float = 2.0,
    sample_steps: int = 32,
    fake_stereo: bool = True,
    cancel_check: Optional[Callable[[], bool]] = None,
) -> Path:
    """执行推理生成音频
    
    Args:
        cancel_check: 可选的取消检查函数，如果返回 True，则中断推理
    """
    with torch.inference_mode():
        # 在开始推理前检查取消状态
        if cancel_check and cancel_check():
            raise RuntimeError("Inference cancelled")
        
        # 启用进度条以在 stdout 显示进度
        print(f"Starting inference: {int(duration * 5)} blocks, {sample_steps} steps", flush=True)
        latent = model.sample_block_cache(
            text=text.unsqueeze(0),
            duration=int(duration * 5),
            style_prompt=style_prompt.unsqueeze(0),
            steps=sample_steps,
            cfg_strength=cfg_strength,
            process_bar=True,  # 启用进度条
        )
        print("Inference completed, decoding audio...", flush=True)
        
        # 在解码前再次检查取消状态
        if cancel_check and cancel_check():
            raise RuntimeError("Inference cancelled")
        latent = latent.transpose(1, 2)
        print("Decoding audio...", flush=True)
        audio = decoder.decode_audio(latent, overlap=5, chunk_size=20)
        
        num_channels = 1
        audio = audio.float().cpu().numpy().squeeze()[None, :]
        if fake_stereo:
            print("Creating fake stereo...", flush=True)
            audio = make_fake_stereo(audio, decoder.h.sampling_rate)
            num_channels = 2
        
        print(f"Saving audio to {output_path}...", flush=True)
        with pedalboard.io.AudioFile(str(output_path), "w", decoder.h.sampling_rate, num_channels) as f:
            f.write(audio)
        print(f"Audio saved successfully: {output_path}", flush=True)
    
    return output_path

