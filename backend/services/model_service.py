"""
模型管理服务
"""
import os
import logging
from pathlib import Path
from typing import Dict, Optional, List
from huggingface_hub import hf_hub_download, snapshot_download
import torch

logger = logging.getLogger(__name__)


class ModelService:
    """模型管理服务"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.model_dir = self.base_dir / "models"
        self.ckpt_dir = self.model_dir / "ckpt"
        self.mulan_dir = self.model_dir / "mulan"
        
        # 创建目录
        self.ckpt_dir.mkdir(parents=True, exist_ok=True)
        self.mulan_dir.mkdir(parents=True, exist_ok=True)
        
        self._diffrhythm2_repo = "ASLP-lab/DiffRhythm2"
        self._mulan_repo = "OpenMuQ/MuQ-MuLan-large"
        
        self._loaded_models = {}
    
    def get_model_status(self) -> Dict:
        """获取模型状态"""
        status = {
            "diffrhythm2": {
                "downloaded": False,
                "path": None,
                "size": None
            },
            "mulan": {
                "downloaded": False,
                "path": None,
                "size": None
            }
        }
        
        # 检查 DiffRhythm2 模型
        ckpt_files = list(self.ckpt_dir.glob("*.safetensors")) + list(self.ckpt_dir.glob("*.pth"))
        if ckpt_files:
            status["diffrhythm2"]["downloaded"] = True
            status["diffrhythm2"]["path"] = str(ckpt_files[0])
            status["diffrhythm2"]["size"] = sum(f.stat().st_size for f in ckpt_files) / (1024**3)  # GB
        
        # 检查 MuQ-MuLan 模型
        mulan_files = list(self.mulan_dir.rglob("*.safetensors")) + list(self.mulan_dir.rglob("*.pth"))
        if mulan_files:
            status["mulan"]["downloaded"] = True
            status["mulan"]["path"] = str(self.mulan_dir)
            status["mulan"]["size"] = sum(f.stat().st_size for f in mulan_files) / (1024**3)  # GB
        
        return status
    
    def download_model(
        self,
        model_type: str = "diffrhythm2",
        progress_callback: Optional[callable] = None
    ) -> Dict:
        """下载模型"""
        if model_type == "diffrhythm2":
            return self._download_diffrhythm2(progress_callback)
        elif model_type == "mulan":
            return self._download_mulan(progress_callback)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
    
    def _download_diffrhythm2(self, progress_callback: Optional[callable] = None) -> Dict:
        """下载 DiffRhythm2 模型"""
        try:
            logger.info(f"Downloading DiffRhythm2 model from {self._diffrhythm2_repo}")
            
            # 下载模型文件
            model_path = snapshot_download(
                repo_id=self._diffrhythm2_repo,
                local_dir=str(self.ckpt_dir),
                local_dir_use_symlinks=False
            )
            
            logger.info(f"DiffRhythm2 model downloaded to {model_path}")
            return {
                "success": True,
                "path": model_path,
                "message": "Model downloaded successfully"
            }
        except Exception as e:
            logger.error(f"Failed to download DiffRhythm2 model: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to download model"
            }
    
    def _download_mulan(self, progress_callback: Optional[callable] = None) -> Dict:
        """下载 MuQ-MuLan 模型"""
        try:
            logger.info(f"Downloading MuQ-MuLan model from {self._mulan_repo}")
            
            model_path = snapshot_download(
                repo_id=self._mulan_repo,
                local_dir=str(self.mulan_dir),
                local_dir_use_symlinks=False
            )
            
            logger.info(f"MuQ-MuLan model downloaded to {model_path}")
            return {
                "success": True,
                "path": model_path,
                "message": "Model downloaded successfully"
            }
        except Exception as e:
            logger.error(f"Failed to download MuQ-MuLan model: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to download model"
            }
    
    def estimate_hardware_requirements(
        self,
        model_type: str = "diffrhythm2",
        precision: str = "fp16"
    ) -> Dict:
        """评估模型硬件需求"""
        status = self.get_model_status()
        
        if model_type == "diffrhythm2":
            model_info = status["diffrhythm2"]
        elif model_type == "mulan":
            model_info = status["mulan"]
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if not model_info["downloaded"]:
            # 使用默认估算
            model_size = 2.0  # GB
        else:
            model_size = model_info["size"] or 2.0
        
        # 精度系数
        precision_multiplier = {
            "fp32": 1.0,
            "fp16": 0.5,
            "int8": 0.25
        }.get(precision, 0.5)
        
        # 估算显存需求
        vram_required = model_size * precision_multiplier + 1.0  # 基础开销
        
        return {
            "model_size_gb": model_size,
            "vram_required_gb": vram_required,
            "precision": precision,
            "recommended_batch_size": self._recommend_batch_size(vram_required)
        }
    
    def _recommend_batch_size(self, vram_required: float) -> int:
        """推荐批处理大小"""
        if vram_required < 4:
            return 4
        elif vram_required < 6:
            return 2
        else:
            return 1
    
    def load_model(
        self,
        model_type: str = "diffrhythm2",
        device: str = "cuda",
        precision: str = "fp16"
    ) -> Optional[object]:
        """加载模型到内存"""
        model_key = f"{model_type}_{device}_{precision}"
        
        if model_key in self._loaded_models:
            logger.info(f"Model {model_key} already loaded")
            return self._loaded_models[model_key]
        
        # 这里应该调用实际的模型加载逻辑
        # 暂时返回 None，实际实现需要根据 inference.py 中的逻辑
        logger.info(f"Loading model {model_type} on {device} with {precision}")
        
        # TODO: 实现实际的模型加载
        # model = prepare_model(...)
        # self._loaded_models[model_key] = model
        
        return None
    
    def unload_model(self, model_type: str = "diffrhythm2"):
        """卸载模型"""
        keys_to_remove = [k for k in self._loaded_models.keys() if k.startswith(model_type)]
        for key in keys_to_remove:
            del self._loaded_models[key]
            logger.info(f"Unloaded model {key}")
        
        # 清理 GPU 缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# 全局实例
_model_service: Optional[ModelService] = None


def get_model_service(base_dir: Optional[Path] = None) -> ModelService:
    """获取模型服务单例"""
    global _model_service
    if _model_service is None:
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent / "Build"
        _model_service = ModelService(base_dir)
    return _model_service

