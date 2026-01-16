#!/bin/bash
# DiffRhythm2 GUI 项目初始化设置脚本
# 所有环境隔离在项目目录内

set -e  # 遇到错误立即退出

# 获取脚本所在目录的父目录（项目根目录）
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 开始设置 DiffRhythm2 GUI 项目..."
echo "📁 项目根目录: $PROJECT_ROOT"
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js 18+"
    echo "   访问: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本过低，需要 18+，当前版本: $(node --version)"
    exit 1
fi
echo "✅ Node.js 版本: $(node --version)"

# 检查并安装 uv
if ! command -v uv &> /dev/null; then
    echo "📦 安装 uv (快速 Python 包管理器)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    if ! command -v uv &> /dev/null; then
        echo "❌ uv 安装失败，请手动安装: https://github.com/astral-sh/uv"
        exit 1
    fi
else
    echo "✅ uv 已安装: $(uv --version)"
fi

# 检查并安装 espeak (phonemizer 依赖)
echo ""
echo "🔊 检查 espeak (phonemizer 依赖)..."
if ! command -v espeak &> /dev/null; then
    echo "📦 安装 espeak..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install espeak
        else
            echo "⚠️  请先安装 Homebrew，然后运行: brew install espeak"
            echo "   或访问: https://brew.sh/"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y espeak espeak-data libespeak1 libespeak-dev
        elif command -v yum &> /dev/null; then
            sudo yum install -y espeak espeak-devel
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm espeak
        else
            echo "⚠️  请手动安装 espeak 包"
        fi
    else
        echo "⚠️  无法自动检测系统类型，请手动安装 espeak"
    fi
    
    if ! command -v espeak &> /dev/null; then
        echo "❌ espeak 安装失败，请手动安装"
        echo "   macOS: brew install espeak"
        echo "   Ubuntu/Debian: sudo apt-get install espeak espeak-data libespeak1 libespeak-dev"
        echo "   CentOS/RHEL: sudo yum install espeak espeak-devel"
        echo "   Arch: sudo pacman -S espeak"
        exit 1
    fi
else
    echo "✅ espeak 已安装: $(espeak --version 2>&1 | head -1)"
fi

# 使用 uv 安装 Python 3.12
echo ""
echo "🐍 使用 uv 安装 Python 3.12..."
uv python install 3.12
if [ $? -ne 0 ]; then
    echo "⚠️  Python 3.12 安装失败，尝试使用系统 Python 3.12..."
    if command -v python3.12 &> /dev/null; then
        PYTHON_CMD="python3.12"
        echo "✅ 使用系统 Python 3.12: $(python3.12 --version)"
    else
        echo "❌ 无法找到或安装 Python 3.12"
        echo "   请手动安装 Python 3.12: https://www.python.org/downloads/"
        exit 1
    fi
else
    PYTHON_CMD="uv python pin 3.12"
    echo "✅ Python 3.12 已安装"
fi

# 检查并安装 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "📦 安装 pnpm..."
    npm install -g pnpm
else
    echo "✅ pnpm 已安装: $(pnpm --version)"
fi

# 设置前端环境（在项目目录内）
echo ""
echo "📦 安装前端依赖..."
cd "$PROJECT_ROOT/frontend"
if [ -d "node_modules" ]; then
    echo "⚠️  node_modules 已存在，跳过安装"
else
    pnpm install
    echo "✅ 前端依赖安装完成"
fi
cd "$PROJECT_ROOT"

# 设置 Python 虚拟环境（在项目目录内，使用 uv）
echo ""
echo "🐍 使用 uv 设置 Python 3.12 虚拟环境（在 backend/.venv）..."
cd "$PROJECT_ROOT/backend"

# 删除旧的虚拟环境
if [ -d "venv" ]; then
    echo "🗑️  删除旧的 venv 虚拟环境..."
    rm -rf venv
fi
if [ -d ".venv" ]; then
    echo "🗑️  删除旧的 .venv 虚拟环境..."
    rm -rf .venv
fi

VENV_PATH=".venv"

# 使用 uv 创建虚拟环境（Python 3.12）
echo "创建 Python 3.12 虚拟环境..."
uv venv --python 3.12 "$VENV_PATH"
if [ $? -ne 0 ]; then
    echo "⚠️  uv venv 创建失败，尝试使用传统方法..."
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv "$VENV_PATH"
    else
        echo "❌ 无法创建虚拟环境，请确保 Python 3.12 已安装"
        exit 1
    fi
fi
echo "✅ 虚拟环境创建成功: backend/$VENV_PATH"

# 使用 uv 安装依赖（更快）
echo ""
echo "📦 使用 uv 安装后端依赖..."
if [ -f "requirements.txt" ]; then
    # 使用 uv pip install，指定 Python 解释器路径
    uv pip install --python "$VENV_PATH/bin/python" -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 后端依赖安装完成（使用 uv）"
    else
        echo "⚠️  uv 安装失败，尝试使用传统 pip..."
        source "$VENV_PATH/bin/activate"
        pip install --upgrade pip --quiet
        pip install -r requirements.txt
        deactivate
        echo "✅ 后端依赖安装完成（使用 pip）"
    fi
else
    echo "⚠️  requirements.txt 不存在，跳过依赖安装"
fi

cd "$PROJECT_ROOT"

# 创建必要的目录结构（在项目目录内）
echo ""
echo "📁 创建必要的目录结构..."
mkdir -p Build/logs
mkdir -p Build/outputs
mkdir -p Build/models/ckpt
mkdir -p Build/models/mulan
mkdir -p Build/cache
mkdir -p Build/uploads/prompts
echo "✅ 目录结构创建完成"

# 创建 .env 示例文件（如果不存在）
echo ""
echo "📝 检查环境变量文件..."
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Paths to Build directory components
MODEL_CACHE_DIR=./Build/models/ckpt
OUTPUT_DIR=./Build/outputs
CACHE_DIR=./Build/cache
LOG_DIR=./Build/logs
UPLOAD_DIR=./Build/uploads
EOF
    echo "✅ 创建 backend/.env 示例文件"
else
    echo "⚠️  backend/.env 已存在，跳过创建"
fi

if [ ! -f "frontend/web/.env.local" ]; then
    cat > frontend/web/.env.local << 'EOF'
# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
    echo "✅ 创建 frontend/web/.env.local 示例文件"
else
    echo "⚠️  frontend/web/.env.local 已存在，跳过创建"
fi

echo ""
echo "✅ 设置完成！"
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 启动后端服务："
echo "   ./scripts/start-backend.sh"
echo "   或"
echo "   cd backend && source .venv/bin/activate && python main.py"
echo ""
echo "2. 启动 Web 前端（新终端）："
echo "   cd frontend && pnpm --filter web dev"
echo "   然后访问: http://localhost:3000"
echo ""
echo "3. 启动桌面应用（可选，新终端）："
echo "   cd frontend && pnpm --filter desktop tauri:dev"
echo ""
echo "📚 更多信息请查看 README.md"

