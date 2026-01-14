"""
音乐生成 API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Optional
from backend.services.task_service import get_task_service
from backend.utils.validation import GenerateRequest
from pydantic import ValidationError

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate")
async def generate_music(
    song_name: str = Form(...),
    lyrics: str = Form(...),
    style_prompt: Optional[str] = Form(None),
    style_audio: Optional[UploadFile] = File(None),
    precision: str = Form("fp16"),
    batch_size: int = Form(1)
) -> Dict:
    """生成音乐"""
    try:
        # 验证输入
        try:
            request_data = GenerateRequest(
                song_name=song_name,
                lyrics=lyrics,
                style_prompt=style_prompt,
                style_audio_path=None,  # Will be set after file upload
                precision=precision,
                batch_size=batch_size
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=f"Validation error: {e.errors()}")
        
        if not style_prompt and not style_audio:
            raise HTTPException(status_code=400, detail="Either style_prompt or style_audio is required")
        
        # 创建生成任务
        task_service = get_task_service()
        
        params = {
            "song_name": request_data.song_name,
            "lyrics": request_data.lyrics,
            "style_prompt": request_data.style_prompt,
            "style_audio_path": None,  # Will be set after file upload
            "precision": request_data.precision,
            "batch_size": request_data.batch_size
        }
        
        # 如果有音频文件，保存它
        if style_audio:
            from backend.services.file_service import get_file_service
            from pathlib import Path
            
            base_dir = Path(__file__).parent.parent.parent / "Build"
            file_service = get_file_service(base_dir)
            
            file_content = await style_audio.read()
            file_info = file_service.save_uploaded_file(
                file_content,
                style_audio.filename or "style_audio.wav",
                file_type="prompt"
            )
            params["style_audio_path"] = file_info["path"]
        
        task_id = task_service.create_task("generate", params)
        
        return {
            "task_id": task_id,
            "message": "Generation task created"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

