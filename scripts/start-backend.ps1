# 启动后端服务脚本 (PowerShell)

$ErrorActionPreference = "Stop"

# 获取脚本所在目录的父目录（项目根目录）
# 使用 $MyInvocation.MyCommand.Path 确保无论从哪里调用都能正确获取脚本位置
$scriptPath = $MyInvocation.MyCommand.Path
if (-not $scriptPath) {
    # 如果通过相对路径调用且找不到，尝试查找脚本
    $invocationName = $MyInvocation.InvocationName
    if ($invocationName -and $invocationName -ne ".") {
        # 尝试从当前目录和父目录查找
        $currentDir = Get-Location
        $possiblePaths = @(
            "$currentDir\$invocationName",
            "$currentDir\scripts\$invocationName",
            "$currentDir\..\scripts\$invocationName"
        )
        foreach ($path in $possiblePaths) {
            if (Test-Path $path) {
                $scriptPath = (Resolve-Path $path).Path
                break
            }
        }
    }
}

if (-not $scriptPath) {
    Write-Host "❌ 无法确定脚本位置。请使用以下方式运行：" -ForegroundColor Red
    Write-Host "   从项目根目录: .\scripts\start-backend.ps1" -ForegroundColor Yellow
    Write-Host "   或从 scripts 目录: .\start-backend.ps1" -ForegroundColor Yellow
    exit 1
}

$PROJECT_ROOT = Split-Path -Parent (Split-Path -Parent $scriptPath)

# 验证项目根目录是否正确
if (-not (Test-Path (Join-Path $PROJECT_ROOT "backend\main.py"))) {
    Write-Host "❌ 无法确定项目根目录。请确保在正确的项目目录中运行此脚本。" -ForegroundColor Red
    Write-Host "   项目根目录应该是包含 backend 和 scripts 目录的目录。" -ForegroundColor Yellow
    exit 1
}

Set-Location $PROJECT_ROOT

# 检查 Python 虚拟环境
$venvPath = $null
$venvActivatePath = $null
if (Test-Path (Join-Path $PROJECT_ROOT "backend\.venv\Scripts\Activate.ps1")) {
    $venvActivatePath = Join-Path $PROJECT_ROOT "backend\.venv\Scripts\Activate.ps1"
    $venvPath = Join-Path $PROJECT_ROOT "backend\.venv"
} elseif (Test-Path (Join-Path $PROJECT_ROOT "backend\venv\Scripts\Activate.ps1")) {
    $venvActivatePath = Join-Path $PROJECT_ROOT "backend\venv\Scripts\Activate.ps1"
    $venvPath = Join-Path $PROJECT_ROOT "backend\venv"
} else {
    Write-Host "❌ Python 虚拟环境未找到。请先运行 setup.ps1" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境（使用点源操作符，并传递完整路径）
Write-Host "✅ 激活虚拟环境: $venvPath" -ForegroundColor Green
. $venvActivatePath

# 关键修复：确保 Python 能 import backend（项目根目录必须在 sys.path 里）
# Windows 上 PYTHONPATH 用 ; 分隔
if ($env:PYTHONPATH) {
    $env:PYTHONPATH = $PROJECT_ROOT + ';' + $env:PYTHONPATH
} else {
    $env:PYTHONPATH = $PROJECT_ROOT
}

# 启动 Python 服务
Write-Host "🚀 启动 FastAPI 服务..." -ForegroundColor Green
Write-Host "   访问地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   API 文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "   按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

# 关键修复：从项目根目录用模块方式启动（避免 import 路径问题）
python -m backend.main

