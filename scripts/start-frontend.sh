#!/bin/bash
# 同时启动 Web 和桌面应用（开发模式）

# 获取脚本的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 切换到项目根目录
cd "$PROJECT_ROOT" || {
    echo "Error: Cannot change to project root directory: $PROJECT_ROOT"
    exit 1
}

echo "🎨 启动前端应用（Web + Desktop）..."
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

# 启动 Web 和 Desktop（在后台）
echo "🚀 启动 Web 应用（http://localhost:3000）..."
cd "$PROJECT_ROOT/frontend"
pnpm --filter web dev &
WEB_PID=$!

echo "🚀 启动桌面应用..."
pnpm --filter desktop tauri:dev &
DESKTOP_PID=$!

echo ""
echo "✅ 前端应用已启动"
echo "   Web: http://localhost:3000 (PID: $WEB_PID)"
echo "   Desktop: 正在启动 (PID: $DESKTOP_PID)"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "kill $WEB_PID $DESKTOP_PID 2>/dev/null; exit" INT TERM
wait

