"""
文件管理服务
"""
import logging
import shutil
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class FileService:
    """文件管理服务"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.uploads_dir = self.base_dir / "uploads" / "prompts"
        self.outputs_dir = self.base_dir / "outputs"
        self.temp_dir = self.base_dir / "cache" / "temp"
        
        # 创建目录
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        file_type: str = "prompt"
    ) -> Dict:
        """保存上传的文件"""
        if file_type == "prompt":
            target_dir = self.uploads_dir
        else:
            target_dir = self.temp_dir
        
        # 生成唯一文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        unique_filename = f"{timestamp}_{safe_filename}"
        file_path = target_dir / unique_filename
        
        # 保存文件
        file_path.write_bytes(file_content)
        
        logger.info(f"Saved uploaded file to {file_path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "filename": unique_filename,
            "size": len(file_content)
        }
    
    def save_output_file(
        self,
        file_content: bytes,
        filename: str
    ) -> Dict:
        """保存生成的输出文件"""
        file_path = self.outputs_dir / filename
        file_path.write_bytes(file_content)
        
        logger.info(f"Saved output file to {file_path}")
        
        return {
            "success": True,
            "path": str(file_path),
            "filename": filename,
            "size": len(file_content)
        }
    
    def get_file_path(self, filename: str, file_type: str = "output") -> Optional[Path]:
        """获取文件路径"""
        if file_type == "output":
            file_path = self.outputs_dir / filename
        elif file_type == "prompt":
            file_path = self.uploads_dir / filename
        else:
            file_path = self.temp_dir / filename
        
        if file_path.exists():
            return file_path
        return None
    
    def delete_file(self, filename: str, file_type: str = "output") -> bool:
        """删除文件"""
        file_path = self.get_file_path(filename, file_type)
        if file_path and file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted file {file_path}")
            return True
        return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """清理临时文件"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        cleaned = 0
        for file_path in self.temp_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} temporary files")
        
        return cleaned
    
    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        def get_dir_size(path: Path) -> int:
            total = 0
            if path.exists():
                for file in path.rglob("*"):
                    if file.is_file():
                        total += file.stat().st_size
            return total
        
        return {
            "uploads_size": get_dir_size(self.uploads_dir) / (1024**2),  # MB
            "outputs_size": get_dir_size(self.outputs_dir) / (1024**2),  # MB
            "temp_size": get_dir_size(self.temp_dir) / (1024**2),  # MB
            "uploads_count": len(list(self.uploads_dir.glob("*"))) if self.uploads_dir.exists() else 0,
            "outputs_count": len(list(self.outputs_dir.glob("*"))) if self.outputs_dir.exists() else 0
        }


# 全局实例
_file_service: Optional[FileService] = None


def get_file_service(base_dir: Optional[Path] = None) -> FileService:
    """获取文件服务单例"""
    global _file_service
    if _file_service is None:
        if base_dir is None:
            base_dir = Path(__file__).parent.parent.parent / "Build"
        _file_service = FileService(base_dir)
    return _file_service

