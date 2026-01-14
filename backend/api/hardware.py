"""
硬件相关 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from backend.services.hardware_service import get_hardware_service

router = APIRouter(prefix="/api/hardware", tags=["hardware"])


@router.get("/info")
async def get_hardware_info() -> Dict:
    """获取硬件信息"""
    try:
        hardware_service = get_hardware_service()
        return hardware_service.get_hardware_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/estimate")
async def estimate_hardware_pressure(
    model_size_gb: float = 2.0,
    batch_size: int = 1,
    precision: str = "fp16"
) -> Dict:
    """预估硬件压力"""
    try:
        hardware_service = get_hardware_service()
        return hardware_service.estimate_hardware_pressure(
            model_size_gb=model_size_gb,
            batch_size=batch_size,
            precision=precision
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def get_optimization_config(
    model_size_gb: float = 2.0
) -> Dict:
    """获取优化配置"""
    try:
        hardware_service = get_hardware_service()
        return hardware_service.get_optimization_config(model_size_gb=model_size_gb)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_realtime_stats() -> Dict:
    """获取实时硬件统计"""
    try:
        hardware_service = get_hardware_service()
        return hardware_service.get_realtime_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

