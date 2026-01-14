"""
历史记录管理服务
"""
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import aiosqlite

logger = logging.getLogger(__name__)


class HistoryService:
    """历史记录管理服务"""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        # 同步创建表（初始化时）
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                song_name TEXT,
                lyrics TEXT,
                style_prompt TEXT,
                output_path TEXT,
                created_at TEXT,
                duration REAL,
                file_size INTEGER,
                params TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")
    
    async def add_history(
        self,
        song_name: str,
        lyrics: str,
        style_prompt: str,
        output_path: str,
        duration: float,
        file_size: int,
        params: Optional[Dict] = None
    ) -> str:
        """添加历史记录"""
        import uuid
        history_id = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO history (
                    id, song_name, lyrics, style_prompt, output_path,
                    created_at, duration, file_size, params
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                history_id,
                song_name,
                lyrics,
                style_prompt,
                output_path,
                datetime.now().isoformat(),
                duration,
                file_size,
                json.dumps(params or {})
            ))
            await db.commit()
        
        logger.info(f"Added history record {history_id}")
        return history_id
    
    async def get_history(
        self,
        limit: int = 50,
        offset: int = 0,
        search: Optional[str] = None
    ) -> List[Dict]:
        """获取历史记录"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if search:
                query = """
                    SELECT * FROM history
                    WHERE song_name LIKE ? OR lyrics LIKE ?
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                search_pattern = f"%{search}%"
                async with db.execute(query, (search_pattern, search_pattern, limit, offset)) as cursor:
                    rows = await cursor.fetchall()
            else:
                query = """
                    SELECT * FROM history
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """
                async with db.execute(query, (limit, offset)) as cursor:
                    rows = await cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                # 解析 JSON 字段
                if result.get("params"):
                    try:
                        result["params"] = json.loads(result["params"])
                    except:
                        result["params"] = {}
                results.append(result)
            
            return results
    
    async def get_history_by_id(self, history_id: str) -> Optional[Dict]:
        """根据 ID 获取历史记录"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            async with db.execute(
                "SELECT * FROM history WHERE id = ?",
                (history_id,)
            ) as cursor:
                row = await cursor.fetchone()
            
            if row:
                result = dict(row)
                if result.get("params"):
                    try:
                        result["params"] = json.loads(result["params"])
                    except:
                        result["params"] = {}
                return result
        
        return None
    
    async def delete_history(self, history_id: str) -> bool:
        """删除历史记录"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM history WHERE id = ?",
                (history_id,)
            )
            await db.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Deleted history record {history_id}")
                return True
        
        return False
    
    async def get_history_count(self, search: Optional[str] = None) -> int:
        """获取历史记录总数"""
        async with aiosqlite.connect(self.db_path) as db:
            if search:
                async with db.execute(
                    "SELECT COUNT(*) FROM history WHERE song_name LIKE ? OR lyrics LIKE ?",
                    (f"%{search}%", f"%{search}%")
                ) as cursor:
                    row = await cursor.fetchone()
            else:
                async with db.execute("SELECT COUNT(*) FROM history") as cursor:
                    row = await cursor.fetchone()
            
            return row[0] if row else 0


# 全局实例
_history_service: Optional[HistoryService] = None


def get_history_service(db_path: Optional[Path] = None) -> HistoryService:
    """获取历史服务单例"""
    global _history_service
    if _history_service is None:
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "Build" / "cache" / "history.db"
        _history_service = HistoryService(db_path)
    return _history_service

