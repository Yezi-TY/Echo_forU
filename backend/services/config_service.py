"""
配置管理服务
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ConfigService:
    """配置管理服务"""
    
    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
        
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "model": {
                "diffrhythm2_repo": "ASLP-lab/DiffRhythm2",
                "mulan_repo": "OpenMuQ/MuQ-MuLan-large",
                "auto_download": True
            },
            "generation": {
                "default_precision": "fp16",
                "default_batch_size": 1,
                "max_duration": 300  # seconds
            },
            "hardware": {
                "auto_optimize": True,
                "preferred_device": "auto"  # auto, cuda, cpu
            },
            "paths": {
                "model_dir": "./Build/models",
                "output_dir": "./Build/outputs",
                "cache_dir": "./Build/cache",
                "log_dir": "./Build/logs",
                "upload_dir": "./Build/uploads"
            }
        }
    
    def _save_config(self):
        """保存配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.info(f"Config saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get_config(self, key: Optional[str] = None) -> Any:
        """获取配置"""
        if key is None:
            return self._config.copy()
        
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        return value
    
    def update_config(self, key: str, value: Any):
        """更新配置"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self._save_config()
        logger.info(f"Updated config {key} = {value}")
    
    def update_config_dict(self, updates: Dict):
        """批量更新配置"""
        def deep_update(base: Dict, updates: Dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self._config, updates)
        self._save_config()
        logger.info("Updated config with multiple values")


# 全局实例
_config_service: Optional[ConfigService] = None


def get_config_service(config_path: Optional[Path] = None) -> ConfigService:
    """获取配置服务单例"""
    global _config_service
    if _config_service is None:
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "config.json"
        _config_service = ConfigService(config_path)
    return _config_service

