"""
任务队列管理服务
"""
import asyncio
import uuid
import logging
from typing import Dict, Any, Callable, Coroutine, Optional, List
from enum import Enum
from datetime import datetime

from backend.utils.path_utils import get_debug_log_path

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """任务模型"""
    def __init__(self, task_id: str, task_type: str, params: Dict[str, Any]):
        self.id = task_id
        self.type = task_type
        self.params = params
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.message = ""
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class TaskService:
    """任务队列管理服务"""
    
    def __init__(self, max_concurrent: int = 1):
        self.max_concurrent = max_concurrent
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self._worker_running = False
        self._worker_task: Optional[asyncio.Task] = None
    
    async def add_task(
        self,
        task_func: Callable[..., Coroutine[Any, Any, Any]],
        *args,
        **kwargs
    ) -> str:
        """添加异步任务到队列"""
        task_id = str(uuid.uuid4())
        task = Task(task_id, "custom", {"args": args, "kwargs": kwargs})
        self.tasks[task_id] = task
        
        # 创建包装函数来执行任务并更新进度
        async def wrapped_task():
            task.status = TaskStatus.RUNNING
            task.progress = 0.0
            task.message = "Starting task..."
            task.updated_at = datetime.now().isoformat()
            
            try:
                result = await task_func(*args, **kwargs)
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.progress = 1.0
                task.message = "Task completed"
                task.updated_at = datetime.now().isoformat()
                logger.info(f"Task {task_id} completed successfully")
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.message = "Task cancelled"
                task.updated_at = datetime.now().isoformat()
                logger.info(f"Task {task_id} cancelled")
                raise
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.message = f"Task failed: {str(e)}"
                task.updated_at = datetime.now().isoformat()
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                raise
        
        # 立即执行任务（不通过队列，因为我们已经有了异步函数）
        running_task = asyncio.create_task(wrapped_task())
        self.running_tasks[task_id] = running_task
        
        # 等待任务完成或失败时清理
        def cleanup_task():
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        running_task.add_done_callback(lambda _: cleanup_task())
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "type": task.type,
            "status": task.status.value,
            "progress": task.progress,
            "message": task.message,
            "result": task.result,
            "error": task.error,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Dict[str, Any]]:
        """获取所有任务"""
        tasks = list(self.tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        
        return [
            {
                "id": task.id,
                "type": task.type,
                "status": task.status.value,
                "progress": task.progress,
                "message": task.message,
                "created_at": task.created_at,
            }
            for task in tasks
        ]
    
    def cancel_task(self, task_id: str) -> bool:
        """取消任务"""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            task.message = "Task cancelled"
            return True
        elif task.status == TaskStatus.RUNNING:
            # 尝试取消运行中的任务
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
            task.status = TaskStatus.CANCELLED
            task.message = "Task cancelled"
            return True
        
        return False
    
    async def start_worker(self):
        """启动任务工作器（兼容性方法，实际任务直接执行）"""
        if self._worker_running:
            return
        
        self._worker_running = True
        logger.info("Task worker started (tasks execute immediately)")
    
    def update_task_progress(self, task_id: str, progress: float, message: Optional[str] = None):
        """更新任务进度"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.progress = progress
            if message:
                task.message = message
            task.updated_at = datetime.now().isoformat()
            
            # 输出进度到 stdout
            progress_percent = int(progress * 100)
            status_msg = f"[{task_id[:8]}] {progress_percent}% - {message or 'Processing...'}"
            print(status_msg, flush=True)
    
    def create_task(self, task_type: str, params: Dict[str, Any]) -> str:
        """创建任务（同步方法，返回 task_id）"""
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type, params)
        self.tasks[task_id] = task
        
        # 根据任务类型创建对应的异步任务函数
        async def task_executor():
            task.status = TaskStatus.RUNNING
            task.progress = 0.0
            task.message = f"Starting {task_type} task..."
            task.updated_at = datetime.now().isoformat()
            
            try:
                if task_type == "generate":
                    from backend.services.inference_service import get_inference_service
                    from pathlib import Path
                    
                    base_dir = Path(__file__).parent.parent.parent / "Build"
                    inference_service = get_inference_service(base_dir)
                    
                    # 创建进度回调函数，同时检查取消状态
                    def progress_callback(progress: float, message: str):
                        # 检查任务是否已被取消
                        if task_id in self.tasks and self.tasks[task_id].status == TaskStatus.CANCELLED:
                            raise asyncio.CancelledError("Task cancelled by user")
                        self.update_task_progress(task_id, progress, message)
                    
                    result = await inference_service.inference(
                        lyrics=params.get("lyrics", ""),
                        style_prompt=params.get("style_prompt"),
                        style_audio_path=params.get("style_audio_path"),
                        song_name=params.get("song_name", "generated"),
                        precision=params.get("precision", "fp16"),
                        batch_size=params.get("batch_size", 1),
                        max_duration=params.get("max_duration", 300),
                        progress_callback=progress_callback,
                        task_id=task_id,  # 传递 task_id 以便检查取消状态
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
                else:
                    task.status = TaskStatus.FAILED
                    task.error = f"Unknown task type: {task_type}"
                    task.message = f"Unsupported task type: {task_type}"
                    task.updated_at = datetime.now().isoformat()
                    logger.error(f"Task {task_id} failed: Unknown task type {task_type}")
            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
                task.message = "Task cancelled"
                task.updated_at = datetime.now().isoformat()
                logger.info(f"Task {task_id} cancelled")
                raise
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.message = f"Task failed: {str(e)}"
                task.updated_at = datetime.now().isoformat()
                logger.error(f"Task {task_id} failed: {e}", exc_info=True)
                raise
        
        # 在 FastAPI 的异步环境中，直接创建任务
        # FastAPI 运行在 uvicorn 的事件循环中，所以可以直接使用 create_task
        try:
            loop = asyncio.get_running_loop()
            running_task = loop.create_task(task_executor())
        except RuntimeError:
            # 如果没有运行中的事件循环，使用 get_event_loop
            loop = asyncio.get_event_loop()
            running_task = loop.create_task(task_executor())
        
        self.running_tasks[task_id] = running_task
        
        # 等待任务完成或失败时清理
        def cleanup_task():
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
        
        running_task.add_done_callback(lambda _: cleanup_task())
        
        return task_id


# 全局实例
_task_service: Optional[TaskService] = None


def get_task_service() -> TaskService:
    """获取任务服务单例"""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
    return _task_service
