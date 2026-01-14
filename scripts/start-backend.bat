@echo off
REM 启动后端服务脚本 (Windows)

cd /d "%~dp0\.."

REM 检查 Python 虚拟环境
if exist "backend\venv\Scripts\activate.bat" (
    call backend\venv\Scripts\activate.bat
) else if exist "backend\.venv\Scripts\activate.bat" (
    call backend\.venv\Scripts\activate.bat
) else (
    echo Python virtual environment not found. Please run setup.bat first.
    exit /b 1
)

REM 启动 FastAPI 服务
cd backend
python main.py

