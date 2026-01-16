"""
音乐生成 API 路由
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Optional
import uuid
import asyncio
import logging
from datetime import datetime
from backend.services.task_service import get_task_service, Task, TaskStatus
from backend.utils.validation import GenerateRequest
from pydantic import ValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])


@router.post("/generate")
async def generate_music(
    song_name: str = Form(...),
    lyrics: str = Form(...),
    style_prompt: Optional[str] = Form(None),
    style_audio: Optional[UploadFile] = File(None),
    precision: str = Form("fp16"),
    batch_size: str = Form("1")  # 先接收字符串，然后转换
) -> Dict:
    """生成音乐 - 立即返回 task_id，不等待任务执行"""
    
    try:
        # 转换 batch_size 为整数
        try:
            batch_size_int = int(batch_size)
        except (ValueError, TypeError):
            batch_size_int = 1
        # 验证输入
        try:
            request_data = GenerateRequest(
                song_name=song_name,
                lyrics=lyrics,
                style_prompt=style_prompt,
                style_audio_path=None,  # Will be set after file upload
                precision=precision,
                batch_size=batch_size_int
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
            "batch_size": batch_size_int
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
        
        # 创建任务（应该很快，只是创建任务对象和启动异步执行）
        # 使用 asyncio.create_task 在后台启动任务，不阻塞响应
        task_id = str(uuid.uuid4())
        task = Task(task_id, "generate", params)
        task_service.tasks[task_id] = task
        
        # 在后台启动任务执行，不等待
        async def start_task_background():
            try:
                # 调用原来的 create_task 逻辑，但以异步方式
                from backend.services.inference_service import get_inference_service
                from pathlib import Path
                
                base_dir = Path(__file__).parent.parent.parent / "Build"
                inference_service = get_inference_service(base_dir)
                
                task.status = TaskStatus.RUNNING
                task.progress = 0.0
                task.message = "Starting generation task..."
                task.updated_at = datetime.now().isoformat()
                
                def progress_callback(progress: float, message: str):
                    if task_id in task_service.tasks and task_service.tasks[task_id].status == TaskStatus.CANCELLED:
                        raise asyncio.CancelledError("Task cancelled by user")
                    task_service.update_task_progress(task_id, progress, message)
                
                result = await inference_service.inference(
                    lyrics=params.get("lyrics", ""),
                    style_prompt=params.get("style_prompt"),
                    style_audio_path=params.get("style_audio_path"),
                    song_name=params.get("song_name", "generated"),
                    precision=params.get("precision", "fp16"),
                    batch_size=params.get("batch_size", 1),
                    max_duration=params.get("max_duration", 300),
                    progress_callback=progress_callback,
                    task_id=task_id,
                )
                
                if result.get("success"):
                    task.result = result
                    task.status = TaskStatus.COMPLETED
                    task.progress = 1.0
                    task.message = "Generation completed"
                    task.updated_at = datetime.now().isoformat()
                    logger.info(f"Task {task_id} completed successfully")
                else:
                    task.status = TaskStatus.FAILED
                    task.error = result.get("error", "Unknown error")
                    task.message = result.get("message", "Generation failed")
                    task.updated_at = datetime.now().isoformat()
                    logger.error(f"Task {task_id} failed: {task.error}")
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.message = "Task cancelled"
                task.updated_at = datetime.now().isoformat()
                logger.info(f"Task {task_id} cancelled")
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.message = f"Task failed: {str(e)}"
                task.updated_at = datetime.now().isoformat()
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
        
        # 在后台启动任务，不等待
        # 延迟启动任务，确保响应先返回
        async def delayed_start():
            # 等待一小段时间，确保响应已经返回
            await asyncio.sleep(0.01)
            await start_task_background()
        
        background_task = asyncio.ensure_future(delayed_start())
        task_service.running_tasks[task_id] = background_task
        
        # 准备响应 - 立即返回，不等待任务执行
        response_data = {
            "task_id": task_id,
            "message": "Generation task created"
        }
        
        return response_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_music: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

