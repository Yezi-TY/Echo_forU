#!/bin/bash
# 启动后端服务脚本

# 获取脚本的绝对路径（使用 BASH_SOURCE，这是最可靠的方法）
SCRIPT_PATH="${BASH_SOURCE[0]}"
# 如果是符号链接，获取真实路径
if [ -L "$SCRIPT_PATH" ]; then
    SCRIPT_PATH="$(readlink "$SCRIPT_PATH" 2>/dev/null || echo "$SCRIPT_PATH")"
    # 如果 readlink 返回的是相对路径，需要基于原路径解析
    if [ "${SCRIPT_PATH#/}" = "$SCRIPT_PATH" ]; then
        SCRIPT_PATH="$(dirname "${BASH_SOURCE[0]}")/$SCRIPT_PATH"
    fi
fi

# 获取脚本所在目录的绝对路径
# 先尝试使用 cd + pwd（最可靠）
SCRIPT_DIR=""
if [ -d "$(dirname "$SCRIPT_PATH")" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" 2>/dev/null && pwd)"
fi

# 如果失败，尝试其他方法
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    # 尝试从当前工作目录查找（如果可用）
    if [ -n "$PWD" ] && [ -d "$PWD" ] 2>/dev/null; then
        if [ -f "$PWD/$SCRIPT_PATH" ]; then
            SCRIPT_DIR="$(cd "$PWD/$(dirname "$SCRIPT_PATH")" 2>/dev/null && pwd)"
        fi
    fi
fi

# 如果还是失败，报错
if [ -z "$SCRIPT_DIR" ] || [ ! -d "$SCRIPT_DIR" ]; then
    echo "Error: Cannot determine script directory"
    echo "Script path: $SCRIPT_PATH"
    exit 1
fi

# 获取项目根目录（SCRIPT_DIR 的父目录）
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." 2>/dev/null && pwd)"
if [ -z "$PROJECT_ROOT" ] || [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: Cannot determine project root directory"
    echo "Script dir: $SCRIPT_DIR"
    exit 1
fi

# 验证项目根目录
if [ ! -f "$PROJECT_ROOT/backend/main.py" ]; then
    echo "Error: Cannot find backend/main.py in project root"
    echo "Project root: $PROJECT_ROOT"
    exit 1
fi

# 切换到项目根目录
cd "$PROJECT_ROOT" || {
    echo "Error: Cannot change to project root directory: $PROJECT_ROOT"
    exit 1
}

echo "🚀 启动后端服务..."
echo "📁 项目根目录: $PROJECT_ROOT"
echo ""

# 检查 Python 虚拟环境（优先使用 .venv，这是 uv 创建的）
if [ -d "backend/.venv" ]; then
    source backend/.venv/bin/activate
    echo "✅ 使用虚拟环境: backend/.venv"
elif [ -d "backend/venv" ]; then
    source backend/venv/bin/activate
    echo "✅ 使用虚拟环境: backend/venv"
else
    echo "❌ Python virtual environment not found. Please run setup.sh first."
    exit 1
fi

# 设置 PYTHONPATH 为项目根目录，以便导入 backend 模块
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# 确保 espeak 在 PATH 中（macOS Homebrew 安装位置）
if [ -d "/opt/homebrew/bin" ]; then
    export PATH="/opt/homebrew/bin:$PATH"
elif [ -d "/usr/local/bin" ]; then
    export PATH="/usr/local/bin:$PATH"
fi

echo "🌐 启动 FastAPI 服务..."
echo "   访问地址: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo "   按 Ctrl+C 停止服务"
echo ""

# 启动 FastAPI 服务（从项目根目录运行，这样 backend 模块可以被找到）
# 使用 trap 确保 Ctrl+C 能正确终止进程
trap "echo ''; echo '🛑 正在停止服务...'; kill 0; exit" INT TERM

python -m backend.main

