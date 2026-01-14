"""
硬件检测和优化服务
"""
import logging
import platform
from typing import Dict, Optional, List
from pathlib import Path

try:
    import pynvml
    PYNVML_AVAILABLE = True
except ImportError:
    PYNVML_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

logger = logging.getLogger(__name__)


class HardwareService:
    """硬件检测和优化服务"""
    
    def __init__(self):
        self._gpu_info = None
        self._cpu_info = None
        self._memory_info = None
        self._initialize()
    
    def _initialize(self):
        """初始化硬件检测"""
        if PYNVML_AVAILABLE:
            try:
                pynvml.nvmlInit()
                logger.info("NVIDIA GPU detection initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NVIDIA GPU detection: {e}")
        
        self._detect_gpu()
        self._detect_cpu()
        self._detect_memory()
    
    def _detect_gpu(self) -> Dict:
        """检测 GPU 信息"""
        gpu_info = {
            "available": False,
            "cuda_available": False,
            "gpus": []
        }
        
        # 检测 CUDA 可用性
        if TORCH_AVAILABLE:
            gpu_info["cuda_available"] = torch.cuda.is_available()
            if gpu_info["cuda_available"]:
                gpu_info["available"] = True
                gpu_count = torch.cuda.device_count()
                for i in range(gpu_count):
                    gpu = {
                        "index": i,
                        "name": torch.cuda.get_device_name(i),
                        "memory_total": torch.cuda.get_device_properties(i).total_memory / (1024**3),  # GB
                        "compute_capability": f"{torch.cuda.get_device_properties(i).major}.{torch.cuda.get_device_properties(i).minor}"
                    }
                    gpu_info["gpus"].append(gpu)
        
        # 使用 pynvml 获取更详细信息
        if PYNVML_AVAILABLE and gpu_info["cuda_available"]:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    if i < len(gpu_info["gpus"]):
                        gpu_info["gpus"][i]["memory_free"] = pynvml.nvmlDeviceGetMemoryInfo(handle).free / (1024**3)  # GB
                        gpu_info["gpus"][i]["memory_used"] = pynvml.nvmlDeviceGetMemoryInfo(handle).used / (1024**3)  # GB
                        gpu_info["gpus"][i]["utilization"] = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                        gpu_info["gpus"][i]["temperature"] = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except Exception as e:
                logger.warning(f"Failed to get detailed GPU info: {e}")
        
        self._gpu_info = gpu_info
        return gpu_info
    
    def _detect_cpu(self) -> Dict:
        """检测 CPU 信息"""
        cpu_info = {
            "cores": psutil.cpu_count(logical=False) if PSUTIL_AVAILABLE else None,
            "logical_cores": psutil.cpu_count(logical=True) if PSUTIL_AVAILABLE else None,
            "frequency": psutil.cpu_freq().current if PSUTIL_AVAILABLE and psutil.cpu_freq() else None,
            "usage": psutil.cpu_percent(interval=1) if PSUTIL_AVAILABLE else None,
            "platform": platform.processor() or platform.machine()
        }
        
        self._cpu_info = cpu_info
        return cpu_info
    
    def _detect_memory(self) -> Dict:
        """检测内存信息"""
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            memory_info = {
                "total": memory.total / (1024**3),  # GB
                "available": memory.available / (1024**3),  # GB
                "used": memory.used / (1024**3),  # GB
                "percent": memory.percent
            }
        else:
            memory_info = {
                "total": None,
                "available": None,
                "used": None,
                "percent": None
            }
        
        self._memory_info = memory_info
        return memory_info
    
    def get_hardware_info(self) -> Dict:
        """获取完整硬件信息"""
        return {
            "gpu": self._gpu_info or self._detect_gpu(),
            "cpu": self._cpu_info or self._detect_cpu(),
            "memory": self._memory_info or self._detect_memory()
        }
    
    def estimate_hardware_pressure(
        self,
        model_size_gb: float = 2.0,
        batch_size: int = 1,
        precision: str = "fp16"
    ) -> Dict:
        """预估硬件压力"""
        gpu_info = self._gpu_info or self._detect_gpu()
        
        # 精度系数
        precision_multiplier = {
            "fp32": 1.0,
            "fp16": 0.5,
            "int8": 0.25
        }.get(precision, 0.5)
        
        # 预估显存需求
        estimated_vram = model_size_gb * precision_multiplier * batch_size + 1.0  # 基础开销
        
        # 预估生成时间（基于硬件性能）
        base_time_per_minute = 60  # 秒/分钟音频
        
        if gpu_info["available"] and gpu_info["gpus"]:
            gpu = gpu_info["gpus"][0]
            # 基于 GPU 性能估算
            if gpu["memory_total"] >= 12:
                time_multiplier = 0.5  # 高端 GPU
            elif gpu["memory_total"] >= 8:
                time_multiplier = 1.0  # 中端 GPU
            elif gpu["memory_total"] >= 4:
                time_multiplier = 2.0  # 低端 GPU
            else:
                time_multiplier = 4.0  # 非常低端
        else:
            time_multiplier = 10.0  # CPU 模式
        
        estimated_time = base_time_per_minute * time_multiplier * precision_multiplier
        
        # 检查是否可行
        feasible = True
        warnings = []
        
        if gpu_info["available"] and gpu_info["gpus"]:
            gpu = gpu_info["gpus"][0]
            available_vram = gpu.get("memory_free", gpu["memory_total"] * 0.8)
            if estimated_vram > available_vram:
                feasible = False
                warnings.append(f"预估显存需求 ({estimated_vram:.1f}GB) 超过可用显存 ({available_vram:.1f}GB)")
        else:
            warnings.append("未检测到 GPU，将使用 CPU 模式（速度较慢）")
        
        return {
            "feasible": feasible,
            "estimated_vram_gb": estimated_vram,
            "estimated_time_seconds": estimated_time,
            "warnings": warnings,
            "recommendations": self._generate_recommendations(estimated_vram, gpu_info)
        }
    
    def _generate_recommendations(
        self,
        estimated_vram: float,
        gpu_info: Dict
    ) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if not gpu_info["available"]:
            recommendations.append("建议使用 GPU 以获得更好的性能")
            return recommendations
        
        if gpu_info["gpus"]:
            gpu = gpu_info["gpus"][0]
            available_vram = gpu.get("memory_free", gpu["memory_total"] * 0.8)
            
            if estimated_vram > available_vram:
                recommendations.append("降低批处理大小到 1")
                recommendations.append("使用 FP16 或 INT8 精度")
                recommendations.append("考虑使用 CPU 模式")
            elif gpu["memory_total"] < 6:
                recommendations.append("建议使用 FP16 精度以节省显存")
                recommendations.append("批处理大小建议设为 1-2")
            elif gpu["memory_total"] >= 12:
                recommendations.append("可以使用 FP32 或 FP16 精度")
                recommendations.append("可以增加批处理大小以提高速度")
        
        return recommendations
    
    def get_optimization_config(
        self,
        model_size_gb: float = 2.0
    ) -> Dict:
        """根据硬件自动生成优化配置"""
        gpu_info = self._gpu_info or self._detect_gpu()
        
        config = {
            "precision": "fp16",
            "batch_size": 1,
            "use_gpu": True,
            "gradient_checkpointing": False,
            "cpu_offload": False
        }
        
        if not gpu_info["available"]:
            config["use_gpu"] = False
            config["precision"] = "fp32"  # CPU 不支持 FP16
            return config
        
        if gpu_info["gpus"]:
            gpu = gpu_info["gpus"][0]
            available_vram = gpu.get("memory_free", gpu["memory_total"] * 0.8)
            
            if gpu["memory_total"] >= 12:
                config["precision"] = "fp16"
                config["batch_size"] = 4
            elif gpu["memory_total"] >= 8:
                config["precision"] = "fp16"
                config["batch_size"] = 2
            elif gpu["memory_total"] >= 4:
                config["precision"] = "fp16"
                config["batch_size"] = 1
                config["gradient_checkpointing"] = True
            else:
                config["precision"] = "int8"
                config["batch_size"] = 1
                config["gradient_checkpointing"] = True
                config["cpu_offload"] = True
            
            # 检查显存是否足够
            estimated_vram = model_size_gb * 0.5 * config["batch_size"] + 1.0
            if estimated_vram > available_vram:
                config["batch_size"] = 1
                if estimated_vram > available_vram:
                    config["cpu_offload"] = True
        
        return config
    
    def get_realtime_stats(self) -> Dict:
        """获取实时硬件统计"""
        stats = {
            "gpu": {},
            "cpu": {},
            "memory": {}
        }
        
        if PSUTIL_AVAILABLE:
            stats["cpu"]["usage"] = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            stats["memory"]["used"] = memory.used / (1024**3)
            stats["memory"]["percent"] = memory.percent
        
        if PYNVML_AVAILABLE and self._gpu_info and self._gpu_info["available"]:
            try:
                for i, gpu in enumerate(self._gpu_info["gpus"]):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    
                    stats["gpu"][i] = {
                        "memory_used": memory_info.used / (1024**3),
                        "memory_percent": (memory_info.used / memory_info.total) * 100,
                        "utilization": utilization.gpu,
                        "temperature": pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                    }
            except Exception as e:
                logger.warning(f"Failed to get realtime GPU stats: {e}")
        
        return stats


# 全局实例
_hardware_service: Optional[HardwareService] = None


def get_hardware_service() -> HardwareService:
    """获取硬件服务单例"""
    global _hardware_service
    if _hardware_service is None:
        _hardware_service = HardwareService()
    return _hardware_service

