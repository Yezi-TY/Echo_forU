#!/bin/bash
# 启动后端服务脚本

cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

# 检查 Python 虚拟环境（优先使用 .venv，这是 uv 创建的）
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
elif [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
else
    echo "Python virtual environment not found. Please run setup.sh first."
    exit 1
fi

# 设置 PYTHONPATH 为项目根目录，以便导入 backend 模块
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 启动 FastAPI 服务（从项目根目录运行，这样 backend 模块可以被找到）
cd "$PROJECT_ROOT"
python -m backend.main

