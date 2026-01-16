#!/bin/bash
# 启动 Web 前端（Next.js）脚本

# 获取脚本的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录
cd "$PROJECT_ROOT" || {
    echo "Error: Cannot change to project root directory: $PROJECT_ROOT"
    exit 1
}

echo "🌐 启动 Web 前端..."
echo "📁 项目根目录: $PROJECT_ROOT"
echo ""

# 检查前端依赖是否已安装
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  前端依赖未安装，正在安装..."
    cd "$PROJECT_ROOT/frontend"
    pnpm install
    if [ $? -ne 0 ]; then
        echo "❌ 前端依赖安装失败"
        exit 1
    fi
    cd "$PROJECT_ROOT"
fi

# 检查 pnpm 是否安装
if ! command -v pnpm &> /dev/null; then
    echo "❌ pnpm 未安装，请先运行: npm install -g pnpm"
    exit 1
fi

# 启动 Web 应用
echo "🚀 启动 Next.js Web 应用..."
echo "   访问地址: http://localhost:3000"
echo "   按 Ctrl+C 停止服务"
echo ""

cd "$PROJECT_ROOT/frontend"
pnpm --filter web dev

