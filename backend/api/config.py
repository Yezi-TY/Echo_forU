"""
配置管理 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pathlib import Path
from backend.services.config_service import get_config_service

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("")
async def get_config(key: str = None) -> Dict:
    """获取配置"""
    try:
        config_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "config.json"
        config_service = get_config_service(config_path)
        
        if key:
            value = config_service.get_config(key)
            if value is None:
                raise HTTPException(status_code=404, detail=f"Config key '{key}' not found")
            return {"key": key, "value": value}
        else:
            return config_service.get_config()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("")
async def update_config(
    key: str,
    value: Any
) -> Dict:
    """更新配置"""
    try:
        config_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "config.json"
        config_service = get_config_service(config_path)
        
        config_service.update_config(key, value)
        return {"success": True, "message": "Config updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bulk")
async def update_config_bulk(updates: Dict) -> Dict:
    """批量更新配置"""
    try:
        config_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "config.json"
        config_service = get_config_service(config_path)
        
        config_service.update_config_dict(updates)
        return {"success": True, "message": "Config updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

