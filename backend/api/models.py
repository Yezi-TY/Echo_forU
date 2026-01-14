"""
模型管理 API 路由
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Optional
from pathlib import Path
from backend.services.model_service import get_model_service

router = APIRouter(prefix="/api/models", tags=["models"])


@router.get("/status")
async def get_model_status() -> Dict:
    """获取模型状态"""
    try:
        base_dir = Path(__file__).parent.parent.parent / "Build"
        model_service = get_model_service(base_dir)
        return model_service.get_model_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download")
async def download_model(
    model_type: str = "diffrhythm2",
    background_tasks: BackgroundTasks = None
) -> Dict:
    """下载模型"""
    try:
        base_dir = Path(__file__).parent.parent.parent / "Build"
        model_service = get_model_service(base_dir)
        
        # 在后台下载
        result = model_service.download_model(model_type=model_type)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Download failed"))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/requirements")
async def get_hardware_requirements(
    model_type: str = "diffrhythm2",
    precision: str = "fp16"
) -> Dict:
    """获取模型硬件需求"""
    try:
        base_dir = Path(__file__).parent.parent.parent / "Build"
        model_service = get_model_service(base_dir)
        return model_service.estimate_hardware_requirements(
            model_type=model_type,
            precision=precision
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

