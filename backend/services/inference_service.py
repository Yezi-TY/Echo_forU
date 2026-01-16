"""
推理服务 - 封装 inference.py 逻辑
"""
import logging
from typing import Dict, Optional, Any, Callable
from pathlib import Path
import torch
import os
import re
import random
import numpy as np
import torchaudio
import pedalboard

from backend.services.hardware_service import get_hardware_service
from backend.services.model_service import get_model_service
from backend.utils.path_utils import get_debug_log_path

logger = logging.getLogger(__name__)


class InferenceService:
    """推理服务 - 封装 DiffRhythm2 推理逻辑"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.model_dir = self.base_dir / "models" / "ckpt"
        self.output_dir = self.base_dir / "outputs"
        
        self.hardware_service = get_hardware_service()
        self.model_service = get_model_service(base_dir)
        
        self._loaded_model = None
        self._device = None
        self._precision = None
        self._mulan = None
        self._decoder = None
        self._tokenizer = None
        self._repo_id = "ASLP-lab/DiffRhythm2"
    
    async def prepare_model(
        self,
        precision: str = "fp16",
        device: Optional[str] = None
    ) -> Dict:
        """准备模型（加载模型到内存）"""
        try:
            # 检测硬件并确定设备
            hardware_info = self.hardware_service.get_hardware_info()
            
            if device is None:
                if hardware_info["gpu"]["available"]:
                    device = "cuda"
                else:
                    device = "cpu"
                    precision = "fp32"  # CPU 不支持 FP16
            
            # 根据硬件调整精度
            if device == "cpu":
                precision = "fp32"
            elif precision == "fp16" and not self._check_fp16_support():
                logger.warning("FP16 not supported, falling back to FP32")
                precision = "fp32"
            
            self._device = torch.device(device)
            self._precision = precision
            
            # 加载所有模型
            from backend.utils.inference_utils import prepare_models
            device_torch = torch.device(device)
            self._loaded_model, self._mulan, self._tokenizer, self._decoder = prepare_models(
                repo_id=self._repo_id,
                ckpt_dir=self.model_dir,
                device=device_torch
            )
            
            # 根据精度调整模型
            if device == "cuda" and precision == "fp16":
                self._loaded_model = self._loaded_model.half()
                self._decoder = self._decoder.half()
                # mulan 也需要转换为 FP16 以确保所有模型组件 dtype 一致
                self._mulan = self._mulan.half()
            elif device == "cpu":
                precision = "fp32"  # CPU 必须使用 FP32
            
            logger.info(f"Model prepared on {device} with {precision}")
            
            return {
                "success": True,
                "device": device,
                "precision": precision,
                "message": f"Model loaded on {device} with {precision}"
            }
        except Exception as e:
            logger.error(f"Failed to prepare model: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to load model"
            }
    
    def _check_fp16_support(self) -> bool:
        """检查是否支持 FP16"""
        if not torch.cuda.is_available():
            return False
        try:
            # 检查计算能力
            device_props = torch.cuda.get_device_properties(0)
            compute_capability = device_props.major * 10 + device_props.minor
            return compute_capability >= 70  # Pascal 架构及以上支持 FP16
        except:
            return False
    
    async def inference(
        self,
        lyrics: str,
        style_prompt: Optional[str] = None,
        style_audio_path: Optional[str] = None,
        song_name: str = "generated",
        precision: Optional[str] = None,
        batch_size: int = 1,
        max_duration: int = 300,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        task_id: Optional[str] = None,
    ) -> Dict:
        """执行推理生成音乐"""
        
        try:
            # 确保模型已加载
            if progress_callback:
                progress_callback(0.1, "Preparing model...")
            print("🔧 Preparing model...", flush=True)
            
            if self._loaded_model is None:
                prep_result = await self.prepare_model(
                    precision=precision or self._precision or "fp16"
                )
                if not prep_result["success"]:
                    return prep_result
            
            if progress_callback:
                progress_callback(0.2, "Model prepared, optimizing parameters...")
            print("✅ Model prepared, optimizing parameters...", flush=True)
            
            # 根据硬件自动调整参数
            optimization_config = self.hardware_service.get_optimization_config()
            
            if precision is None:
                precision = optimization_config.get("precision", "fp16")
            if batch_size == 1:
                batch_size = optimization_config.get("batch_size", 1)
            
            # 验证输入
            if not lyrics or not lyrics.strip():
                return {
                    "success": False,
                    "error": "Lyrics is required",
                    "message": "Please provide lyrics"
                }
            
            if not style_prompt and not style_audio_path:
                return {
                    "success": False,
                    "error": "Style prompt or audio is required",
                    "message": "Please provide either style prompt or audio"
                }
            
            if progress_callback:
                progress_callback(0.3, "Processing lyrics...")
            print("📝 Processing lyrics...", flush=True)
            
            # 解析歌词
            from backend.utils.inference_utils import parse_lyrics, run_inference
            lyrics_tokens = parse_lyrics(lyrics, self._tokenizer)
            # lyrics_tensor 保持为 long 类型（token IDs），不需要转换精度
            lyrics_tensor = torch.tensor(sum(lyrics_tokens, []), dtype=torch.long, device=self._device)
            
            if progress_callback:
                progress_callback(0.4, "Processing style prompt...")
            print("🎨 Processing style prompt...", flush=True)
            
            # 处理风格提示
            with torch.no_grad():
                if style_audio_path and Path(style_audio_path).exists():
                    # 从音频文件加载风格
                    prompt_wav, sr = torchaudio.load(style_audio_path)
                    prompt_wav = torchaudio.functional.resample(prompt_wav.to(self._device), sr, 24000)
                    if prompt_wav.shape[1] > 24000 * 10:
                        start = random.randint(0, prompt_wav.shape[1] - 24000 * 10)
                        prompt_wav = prompt_wav[:, start:start+24000*10]
                    prompt_wav = prompt_wav.mean(dim=0, keepdim=True)
                    style_prompt_embed = self._mulan(wavs=prompt_wav)
                elif style_prompt:
                    # 从文本加载风格
                    style_prompt_embed = self._mulan(texts=[style_prompt])
                else:
                    raise ValueError("Either style_prompt or style_audio_path must be provided")
            
            style_prompt_embed = style_prompt_embed.to(self._device).squeeze(0)
            
            # 根据精度调整
            if self._device.type != 'cpu' and precision in ['fp16', 'int8']:
                style_prompt_embed = style_prompt_embed.half()
            
            if progress_callback:
                progress_callback(0.5, "Generating music...")
            print("🎵 Generating music...", flush=True)
            
            # 准备输出路径
            output_filename = f"{song_name}.mp3"
            output_path = self.output_dir / output_filename
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建取消检查函数（如果提供了 task_id）
            cancel_check = None
            if task_id:
                from backend.services.task_service import get_task_service, TaskStatus
                task_service = get_task_service()
                def check_cancelled():
                    task = task_service.tasks.get(task_id)
                    return task and task.status == TaskStatus.CANCELLED
                cancel_check = check_cancelled
            
            # 执行推理
            run_inference(
                model=self._loaded_model,
                decoder=self._decoder,
                text=lyrics_tensor,
                style_prompt=style_prompt_embed,
                duration=min(max_duration, 300),  # 限制最大时长
                output_path=output_path,
                cfg_strength=2.0,
                sample_steps=32,
                fake_stereo=True,
                cancel_check=cancel_check,
            )
            
            if progress_callback:
                progress_callback(0.9, "Finalizing output...")
            
            logger.info(f"Inference completed: {output_path}")
            logger.info(f"Output file exists: {output_path.exists()}, size: {output_path.stat().st_size if output_path.exists() else 0}")
            
            if progress_callback:
                progress_callback(1.0, "Generation completed")
            print(f"✅ Generation completed: {output_path}", flush=True)
            
            return {
                "success": True,
                "output_path": str(output_path),
                "song_name": song_name,
                "message": "Music generated successfully"
            }
        except Exception as e:
            logger.error(f"Inference failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Generation failed"
            }
    
    def unload_model(self):
        """卸载模型释放内存"""
        if self._loaded_model is not None:
            del self._loaded_model
            self._loaded_model = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model unloaded")


# 全局实例
_inference_service: Optional[InferenceService] = None


def get_inference_service(base_dir: Optional[Path] = None) -> InferenceService:
    """获取推理服务单例"""
    global _inference_service
    if _inference_service is None:
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent / "Build"
        _inference_service = InferenceService(base_dir)
    return _inference_service

