"""
路径工具函数 - 统一管理项目路径
"""
from pathlib import Path


def get_project_root() -> Path:
    """获取项目根目录"""
    # 从 backend/utils/path_utils.py 向上三级到达项目根目录
    return Path(__file__).parent.parent.parent


def get_debug_log_path() -> Path:
    """获取调试日志文件路径"""
    project_root = get_project_root()
    return project_root / ".cursor" / "debug.log"

