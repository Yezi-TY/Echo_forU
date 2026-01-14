"""
历史记录 API 路由
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from pathlib import Path
from backend.services.history_service import get_history_service

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
async def get_history(
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None
) -> Dict:
    """获取历史记录"""
    try:
        db_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "history.db"
        history_service = get_history_service(db_path)
        
        records = await history_service.get_history(
            limit=limit,
            offset=offset,
            search=search
        )
        total = await history_service.get_history_count(search=search)
        
        return {
            "records": records,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{history_id}")
async def get_history_by_id(history_id: str) -> Dict:
    """根据 ID 获取历史记录"""
    try:
        db_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "history.db"
        history_service = get_history_service(db_path)
        
        record = await history_service.get_history_by_id(history_id)
        
        if not record:
            raise HTTPException(status_code=404, detail="History record not found")
        
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{history_id}")
async def delete_history(history_id: str) -> Dict:
    """删除历史记录"""
    try:
        db_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "history.db"
        history_service = get_history_service(db_path)
        
        success = await history_service.delete_history(history_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="History record not found")
        
        return {"success": True, "message": "History record deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

