"""
依赖注入 - FastAPI 依赖项
"""
from pathlib import Path
from typing import Annotated
from fastapi import Depends

from backend.services.hardware_service import HardwareService
from backend.services.model_service import ModelService
from backend.services.task_service import TaskService
from backend.services.history_service import HistoryService
from backend.services.config_service import ConfigService
from backend.services.file_service import FileService
from backend.services.inference_service import InferenceService

# 全局服务实例
_hardware_service: HardwareService | None = None
_model_service: ModelService | None = None
_task_service: TaskService | None = None
_history_service: HistoryService | None = None
_config_service: ConfigService | None = None
_file_service: FileService | None = None
_inference_service: InferenceService | None = None


def get_base_dir() -> Path:
    """获取基础目录（Build 目录）"""
    return Path(__file__).parent.parent / "Build"


def get_hardware_service() -> HardwareService:
    """获取硬件服务实例"""
    global _hardware_service
    if _hardware_service is None:
        _hardware_service = HardwareService()
    return _hardware_service


def get_model_service() -> ModelService:
    """获取模型服务实例"""
    global _model_service
    if _model_service is None:
        base_dir = get_base_dir()
        _model_service = ModelService(base_dir)
    return _model_service


def get_task_service() -> TaskService:
    """获取任务服务实例"""
    global _task_service
    if _task_service is None:
        _task_service = TaskService()
        # 启动任务工作器
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_task_service.start_worker())
            else:
                loop.run_until_complete(_task_service.start_worker())
        except RuntimeError:
            # 如果没有事件循环，创建一个新的
            asyncio.run(_task_service.start_worker())
    return _task_service


def get_history_service() -> HistoryService:
    """获取历史记录服务实例"""
    global _history_service
    if _history_service is None:
        base_dir = get_base_dir()
        db_path = base_dir / "cache" / "history.db"
        _history_service = HistoryService(db_path)
    return _history_service


def get_config_service() -> ConfigService:
    """获取配置服务实例"""
    global _config_service
    if _config_service is None:
        base_dir = get_base_dir()
        config_path = base_dir / "cache" / "config.json"
        _config_service = ConfigService(config_path)
    return _config_service


def get_file_service() -> FileService:
    """获取文件服务实例"""
    global _file_service
    if _file_service is None:
        base_dir = get_base_dir()
        upload_dir = base_dir / "uploads"
        output_dir = base_dir / "outputs"
        cache_dir = base_dir / "cache"
        _file_service = FileService(upload_dir, output_dir, cache_dir)
    return _file_service


def get_inference_service() -> InferenceService:
    """获取推理服务实例"""
    global _inference_service
    if _inference_service is None:
        base_dir = get_base_dir()
        _inference_service = InferenceService(base_dir)
    return _inference_service

