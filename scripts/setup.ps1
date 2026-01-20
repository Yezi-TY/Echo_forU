﻿# DiffRhythm2 GUI 项目初始化设置脚本 (PowerShell)
# 所有环境隔离在项目目录内

$ErrorActionPreference = "Stop"

# 控制台编码：
# - 默认用 gbk(936) 适配 Windows PowerShell 5.1/ConsoleHost 的中文显示
# - 如需 UTF-8，可临时设置：$env:ECHO_CONSOLE_ENCODING="utf8"
$preferred = $env:ECHO_CONSOLE_ENCODING
if (-not $preferred) { $preferred = "gbk" }
try {
    if ($preferred -eq "utf8") {
        [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $OutputEncoding = [System.Text.Encoding]::UTF8
        chcp 65001 | Out-Null
    } else {
        $enc936 = [System.Text.Encoding]::GetEncoding(936)
        [Console]::InputEncoding  = $enc936
        [Console]::OutputEncoding = $enc936
        $OutputEncoding = $enc936
        chcp 936 | Out-Null
    }
} catch { }

# 获取脚本所在目录的父目录（项目根目录）
$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $PROJECT_ROOT

Write-Host "开始设置 DiffRhythm2 GUI 项目..." -ForegroundColor Green
Write-Host "项目根目录: $PROJECT_ROOT" -ForegroundColor Cyan
Write-Host ""

# 检查 Node.js
try {
    $nodeVersion = node --version
    if ($LASTEXITCODE -ne 0) { throw "Node.js 未安装" }
    $nodeMajorVersion = [int]($nodeVersion -replace 'v(\d+)\..*', '$1')
    if ($nodeMajorVersion -lt 18) {
        Write-Host "Node.js 版本过低，需要 18+，当前版本: $nodeVersion" -ForegroundColor Red
        Write-Host "访问: https://nodejs.org/" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Node.js 版本: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js 未安装，请先安装 Node.js 18+" -ForegroundColor Red
    Write-Host "访问: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 检查并安装 uv
try {
    $uvVersion = uv --version
    if ($LASTEXITCODE -ne 0) { throw "uv 未安装" }
    Write-Host "uv 已安装: $uvVersion" -ForegroundColor Green
} catch {
    Write-Host "安装 uv (快速 Python 包管理器)..." -ForegroundColor Yellow
    $uvInstallScript = "powershell -ExecutionPolicy Bypass -c `"irm https://astral.sh/uv/install.ps1 | iex`""
    Invoke-Expression $uvInstallScript
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    try {
        $uvVersion = uv --version
        if ($LASTEXITCODE -ne 0) { throw "uv 安装失败" }
        Write-Host "uv 安装成功: $uvVersion" -ForegroundColor Green
    } catch {
        Write-Host "uv 安装失败，请手动安装: https://github.com/astral-sh/uv" -ForegroundColor Red
        Write-Host "或运行: powershell -ExecutionPolicy Bypass -c `"irm https://astral.sh/uv/install.ps1 | iex`"" -ForegroundColor Yellow
        exit 1
    }
}

# 使用 uv 安装 Python 3.12
Write-Host ""
Write-Host "使用 uv 安装 Python 3.12..." -ForegroundColor Yellow
uv python install 3.12
if ($LASTEXITCODE -ne 0) {
    Write-Host "Python 3.12 安装失败，尝试使用系统 Python 3.12..." -ForegroundColor Yellow
    try {
        $pythonVersion = python3.12 --version
        if ($LASTEXITCODE -eq 0) {
            Write-Host "使用系统 Python 3.12: $pythonVersion" -ForegroundColor Green
        } else {
            throw "Python 3.12 未找到"
        }
    } catch {
        Write-Host "无法找到或安装 Python 3.12" -ForegroundColor Red
        Write-Host "请手动安装 Python 3.12: https://www.python.org/downloads/" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "Python 3.12 已安装" -ForegroundColor Green
}

# 检查并安装 pnpm
try {
    $pnpmVersion = pnpm --version
    if ($LASTEXITCODE -ne 0) { throw "pnpm 未安装" }
    Write-Host "pnpm 已安装: $pnpmVersion" -ForegroundColor Green
} catch {
    Write-Host "安装 pnpm..." -ForegroundColor Yellow
    npm install -g pnpm
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pnpm 安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "pnpm 安装完成" -ForegroundColor Green
}

# 设置前端环境
Write-Host ""
Write-Host "安装前端依赖..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\frontend"
if (Test-Path "node_modules") {
    Write-Host "node_modules 已存在，跳过安装" -ForegroundColor Yellow
} else {
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "前端依赖安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "前端依赖安装完成" -ForegroundColor Green
}
Set-Location $PROJECT_ROOT

# 设置 Python 虚拟环境（backend/.venv）
Write-Host ""
Write-Host "设置 Python 3.12 虚拟环境（backend/.venv）..." -ForegroundColor Yellow
Set-Location "$PROJECT_ROOT\backend"

if (Test-Path "venv") { Remove-Item -Recurse -Force "venv" }
if (Test-Path ".venv") { Remove-Item -Recurse -Force ".venv" }

$VENV_PATH = ".venv"
uv venv --python 3.12 $VENV_PATH
if ($LASTEXITCODE -ne 0) {
    Write-Host "uv venv 创建失败，尝试 python -m venv..." -ForegroundColor Yellow
    python3.12 -m venv $VENV_PATH
    if ($LASTEXITCODE -ne 0) {
        Write-Host "无法创建虚拟环境，请确保 Python 3.12 已安装" -ForegroundColor Red
        exit 1
    }
}
Write-Host "虚拟环境创建成功: backend\$VENV_PATH" -ForegroundColor Green

# 安装后端依赖
Write-Host ""
Write-Host "安装后端依赖..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    $pythonExe = Join-Path $VENV_PATH "Scripts\python.exe"
    uv pip install --python $pythonExe -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "uv 安装失败，尝试 pip..." -ForegroundColor Yellow
        . (Join-Path $VENV_PATH "Scripts\Activate.ps1")
        python -m pip install --upgrade pip --quiet
        pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "后端依赖安装失败" -ForegroundColor Red
            exit 1
        }
        if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }
        Write-Host "后端依赖安装完成（pip）" -ForegroundColor Green
    } else {
        Write-Host "后端依赖安装完成（uv）" -ForegroundColor Green
    }
} else {
    Write-Host "requirements.txt 不存在，跳过依赖安装" -ForegroundColor Yellow
}

Set-Location $PROJECT_ROOT

# 创建目录结构
Write-Host ""
Write-Host "创建必要的目录结构..." -ForegroundColor Yellow
$directories = @(
    "Build\logs",
    "Build\outputs",
    "Build\models\ckpt",
    "Build\models\mulan",
    "Build\cache",
    "Build\uploads\prompts"
)
foreach ($dir in $directories) {
    $fullPath = Join-Path $PROJECT_ROOT $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force | Out-Null
    }
}
Write-Host "目录结构创建完成" -ForegroundColor Green

# 创建 .env 示例文件
Write-Host ""
Write-Host "检查环境变量文件..." -ForegroundColor Yellow
if (-not (Test-Path "backend\.env")) {
    @"
# Backend Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Paths to Build directory components
MODEL_CACHE_DIR=./Build/models/ckpt
OUTPUT_DIR=./Build/outputs
CACHE_DIR=./Build/cache
LOG_DIR=./Build/logs
UPLOAD_DIR=./Build/uploads
"@ | Out-File -FilePath "backend\.env" -Encoding utf8
    Write-Host "创建 backend\.env 示例文件" -ForegroundColor Green
} else {
    Write-Host "backend\.env 已存在，跳过创建" -ForegroundColor Yellow
}

if (-not (Test-Path "frontend\web\.env.local")) {
    @"
# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
"@ | Out-File -FilePath "frontend\web\.env.local" -Encoding utf8
    Write-Host "创建 frontend\web\.env.local 示例文件" -ForegroundColor Green
} else {
    Write-Host "frontend\web\.env.local 已存在，跳过创建" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "设置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步：" -ForegroundColor Cyan
Write-Host "1) 启动后端: .\scripts\start-backend.ps1" -ForegroundColor White
Write-Host "2) 启动 Web:  .\scripts\start-web.ps1" -ForegroundColor White
Write-Host "3) 启动桌面: .\scripts\start-desktop.ps1" -ForegroundColor White

