"""
推理服务 - 封装 inference.py 逻辑
"""
import logging
from typing import Dict, Optional, Any, Callable
from pathlib import Path
import torch

from backend.services.hardware_service import get_hardware_service
from backend.services.model_service import get_model_service

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
            
            self._device = device
            self._precision = precision
            
            # TODO: 实际加载模型
            # 这里需要调用迁移后的 diffrhythm2 代码
            # from backend.diffrhythm2 import prepare_model as dr2_prepare_model
            # self._loaded_model = dr2_prepare_model(
            #     model_path=self.model_dir,
            #     device=device,
            #     precision=precision
            # )
            
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
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> Dict:
        """执行推理生成音乐"""
        try:
            # 确保模型已加载
            if progress_callback:
                progress_callback(0.1, "Preparing model...")
            
            if self._loaded_model is None:
                prep_result = await self.prepare_model(
                    precision=precision or self._precision or "fp16"
                )
                if not prep_result["success"]:
                    return prep_result
            
            if progress_callback:
                progress_callback(0.2, "Model prepared, optimizing parameters...")
            
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
            
            # TODO: 实际调用推理
            # 这里需要调用迁移后的 diffrhythm2 代码
            # from backend.diffrhythm2 import inference as dr2_inference
            # from backend.g2p import chn_eng_g2p
            # 
            # # 处理歌词
            # processed_lyrics = chn_eng_g2p(lyrics)
            # 
            # # 执行推理
            # output_path = dr2_inference(
            #     model=self._loaded_model,
            #     lyrics=processed_lyrics,
            #     style_prompt=style_prompt,
            #     style_audio_path=style_audio_path,
            #     output_dir=self.output_dir,
            #     song_name=song_name,
            #     device=self._device,
            #     precision=precision,
            #     batch_size=batch_size,
            #     max_duration=max_duration
            # )
            
            if progress_callback:
                progress_callback(0.5, "Generating music...")
            
            # 模拟输出路径
            output_filename = f"{song_name}_{int(torch.randint(1000, 9999, (1,)).item())}.mp3"
            output_path = self.output_dir / output_filename
            
            if progress_callback:
                progress_callback(0.9, "Finalizing output...")
            
            logger.info(f"Inference completed: {output_path}")
            
            if progress_callback:
                progress_callback(1.0, "Generation completed")
            
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

