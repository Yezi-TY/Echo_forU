"""
文件上传 API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict
from pathlib import Path
from backend.services.file_service import get_file_service

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = "prompt"
) -> Dict:
    """上传文件"""
    try:
        # 验证文件类型
        allowed_types = ["prompt", "temp"]
        if file_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid file_type. Allowed: {allowed_types}")
        
        # 读取文件内容
        file_content = await file.read()
        
        # 保存文件
        base_dir = Path(__file__).parent.parent.parent / "Build"
        file_service = get_file_service(base_dir)
        
        result = file_service.save_uploaded_file(
            file_content,
            file.filename or "uploaded_file",
            file_type=file_type
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

