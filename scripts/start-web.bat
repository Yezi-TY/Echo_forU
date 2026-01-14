@echo off
REM 启动 Web 前端（Next.js）脚本 - Windows

cd /d "%~dp0\.."
set PROJECT_ROOT=%CD%

echo 🌐 启动 Web 前端...
echo 📁 项目根目录: %PROJECT_ROOT%
echo.

REM 检查前端依赖是否已安装
if not exist "frontend\node_modules" (
    echo ⚠️  前端依赖未安装，正在安装...
    cd "%PROJECT_ROOT%\frontend"
    call pnpm install
    if errorlevel 1 (
        echo ❌ 前端依赖安装失败
        exit /b 1
    )
    cd "%PROJECT_ROOT%"
)

REM 检查 pnpm 是否安装
where pnpm >nul 2>&1
if errorlevel 1 (
    echo ❌ pnpm 未安装，请先运行: npm install -g pnpm
    exit /b 1
)

REM 启动 Web 应用
echo 🚀 启动 Next.js Web 应用...
echo    访问地址: http://localhost:3000
echo    按 Ctrl+C 停止服务
echo.

cd "%PROJECT_ROOT%\frontend"
call pnpm --filter web dev

