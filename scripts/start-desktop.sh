#!/bin/bash
# 启动桌面应用（Tauri）脚本

cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

echo "💻 启动桌面应用..."
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

# 检查 Rust 是否安装（Tauri 需要）
if ! command -v cargo &> /dev/null; then
    echo "⚠️  Rust/Cargo 未安装，Tauri 需要 Rust 环境"
    echo "   安装方法: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    echo "   或访问: https://rustup.rs/"
    exit 1
fi

# 启动桌面应用
echo "🚀 启动 Tauri 桌面应用..."
echo "   按 Ctrl+C 停止应用"
echo ""

cd "$PROJECT_ROOT/frontend"
pnpm --filter desktop tauri:dev

