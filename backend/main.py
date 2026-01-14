"""
DiffRhythm2 GUI Backend - FastAPI Server
"""
import os
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import WebSocket, WebSocketDisconnect
import uvicorn

# Import API routers
from backend.api import hardware, models, tasks, history, config, generate, upload

# Configure logging
build_dir = Path(__file__).parent.parent / "Build"
log_dir = build_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Ensure all Build subdirectories exist
(build_dir / "outputs").mkdir(parents=True, exist_ok=True)
(build_dir / "models" / "ckpt").mkdir(parents=True, exist_ok=True)
(build_dir / "models" / "mulan").mkdir(parents=True, exist_ok=True)
(build_dir / "cache").mkdir(parents=True, exist_ok=True)
(build_dir / "uploads" / "prompts").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "backend.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="DiffRhythm2 API",
    description="Backend API for DiffRhythm2 GUI",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "DiffRhythm2 API", "version": "0.1.0"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/api/version")
async def get_version():
    """Get API version"""
    return {"version": "0.1.0"}


# Include API routers
app.include_router(hardware.router)
app.include_router(models.router)
app.include_router(tasks.router)
app.include_router(history.router)
app.include_router(config.router)
app.include_router(generate.router)
app.include_router(upload.router)


# WebSocket for progress updates
@app.websocket("/api/tasks/{task_id}/progress")
async def websocket_progress(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for task progress"""
    await websocket.accept()
    
    try:
        from backend.services.task_service import get_task_service
        
        task_service = get_task_service()
        
        while True:
            task_status = task_service.get_task_status(task_id)
            
            if not task_status:
                await websocket.send_json({"error": "Task not found"})
                break
            
            progress_data = {
                "task_id": task_id,
                "status": task_status["status"],
                "progress": task_status["progress"],
                "message": task_status["message"]
            }
            
            # 如果有输出路径，添加到进度数据中
            if task_status.get("result") and task_status["result"].get("output_path"):
                progress_data["output_path"] = task_status["result"]["output_path"]
            
            await websocket.send_json(progress_data)
            
            if task_status["status"] in ["completed", "failed", "cancelled"]:
                break
            
            import asyncio
            await asyncio.sleep(0.5)  # 每 0.5 秒更新一次
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for task {task_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    # 使用模块路径，从项目根目录运行时可以找到 backend.main
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

