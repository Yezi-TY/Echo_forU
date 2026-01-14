"""
任务管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
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
        task = task_service.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return task.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        
        return [task.to_dict() for task in tasks]
    except Exception as e:
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

