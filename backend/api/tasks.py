"""
任务管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, List, Optional
import asyncio
import json
from backend.services.task_service import get_task_service, TaskStatus

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/create")
async def create_task(
    task_type: str,
    params: Dict
) -> Dict:
    """创建任务"""
    try:
        task_service = get_task_service()
        task_id = task_service.create_task(task_type, params)
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}")
async def get_task(task_id: str) -> Dict:
    """获取任务状态"""
    try:
        task_service = get_task_service()
        task_status = task_service.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task_status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}/stream")
async def stream_task_progress(task_id: str):
    """使用 Server-Sent Events (SSE) 流式传输任务进度"""
    async def event_generator():
        task_service = get_task_service()
        last_status = None
        last_progress = -1
        
        while True:
            task_status = task_service.get_task_status(task_id)
            
            if not task_status:
                yield f"data: {json.dumps({'error': 'Task not found'})}\n\n"
                break
            
            # 只在状态或进度变化时发送事件
            if (task_status['status'] != last_status or 
                task_status['progress'] != last_progress):
                
                progress_data = {
                    "task_id": task_id,
                    "status": task_status['status'],
                    "progress": task_status['progress'],
                    "message": task_status.get('message', ''),
                }
                
                if task_status.get('result') and task_status['result'].get('output_path'):
                    progress_data["output_path"] = task_status['result']['output_path']
                
                yield f"data: {json.dumps(progress_data)}\n\n"
                
                last_status = task_status['status']
                last_progress = task_status['progress']
                
                # 如果任务完成、失败或取消，停止流
                if task_status['status'] in ['completed', 'failed', 'cancelled']:
                    break
            
            # 等待 0.5 秒后再次检查
            await asyncio.sleep(0.5)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("")
async def get_all_tasks(
    status: Optional[str] = None
) -> List[Dict]:
    """获取所有任务"""
    try:
        task_service = get_task_service()
        
        if status:
            task_status = TaskStatus(status)
            tasks = task_service.get_all_tasks(status=task_status)
        else:
            tasks = task_service.get_all_tasks()
        
        return tasks
    except Exception as e:
        logger.error(f"Error in get_all_tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict:
    """取消任务"""
    try:
        task_service = get_task_service()
        success = task_service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Cannot cancel task")
        
        return {"success": True, "message": "Task cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
