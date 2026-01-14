"""
API 输入验证工具
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, validator
from pathlib import Path


class GenerateRequest(BaseModel):
    """生成请求模型"""
    song_name: str = Field(..., min_length=1, max_length=200, description="歌曲名称")
    lyrics: str = Field(..., min_length=1, max_length=10000, description="歌词内容")
    style_prompt: Optional[str] = Field(None, max_length=500, description="风格文本提示")
    style_audio_path: Optional[str] = Field(None, description="风格音频文件路径")
    precision: str = Field("fp16", pattern="^(fp32|fp16|int8)$", description="模型精度")
    batch_size: int = Field(1, ge=1, le=8, description="批处理大小")

    @validator('lyrics')
    def validate_lyrics(cls, v):
        if not v or not v.strip():
            raise ValueError('Lyrics cannot be empty')
        return v.strip()

    @validator('style_audio_path')
    def validate_audio_path(cls, v):
        if v:
            path = Path(v)
            if not path.exists():
                raise ValueError(f'Audio file not found: {v}')
            if not path.suffix.lower() in ['.wav', '.mp3', '.flac', '.ogg']:
                raise ValueError(f'Unsupported audio format: {path.suffix}')
        return v


class TaskCreateRequest(BaseModel):
    """任务创建请求模型"""
    task_type: str = Field(..., pattern="^(generate|download|other)$", description="任务类型")
    params: dict = Field(..., description="任务参数")


class ConfigUpdateRequest(BaseModel):
    """配置更新请求模型"""
    key: str = Field(..., min_length=1, description="配置键")
    value: Any = Field(..., description="配置值")


class HistorySearchRequest(BaseModel):
    """历史记录搜索请求模型"""
    limit: int = Field(50, ge=1, le=100, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")
    search: Optional[str] = Field(None, max_length=200, description="搜索关键词")


class ModelDownloadRequest(BaseModel):
    """模型下载请求模型"""
    model_type: str = Field(..., pattern="^(diffrhythm2|mulan)$", description="模型类型")


class HardwareEstimateRequest(BaseModel):
    """硬件压力预估请求模型"""
    model_size_gb: float = Field(2.0, ge=0.1, le=50.0, description="模型大小（GB）")
    batch_size: int = Field(1, ge=1, le=16, description="批处理大小")
    precision: str = Field("fp16", pattern="^(fp32|fp16|int8)$", description="模型精度")

