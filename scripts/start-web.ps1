﻿﻿# 启动 Web 前端（Next.js）脚本 - PowerShell

$ErrorActionPreference = "Stop"

# 设置控制台输出编码
# 说明：你当前环境是 Windows PowerShell 5.1 + ConsoleHost，从日志看脚本已输出 UTF-8，
# 在这种情况下，改用 GBK(936) 输出反而能在该终端正常显示中文。
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

Write-Host "启动 Web 前端..." -ForegroundColor Green
Write-Host "项目根目录: $PROJECT_ROOT" -ForegroundColor Cyan
Write-Host ""

# 检查前端依赖是否已安装
Set-Location "$PROJECT_ROOT\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "前端依赖未安装，正在安装..." -ForegroundColor Yellow
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "前端依赖安装失败" -ForegroundColor Red
        exit 1
    }
    Write-Host "前端依赖安装完成" -ForegroundColor Green
}

# 检查 web 子项目的 node_modules
if (-not (Test-Path "web\node_modules")) {
    Write-Host "Web 子项目依赖未安装，正在安装..." -ForegroundColor Yellow
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Web 依赖安装失败" -ForegroundColor Red
        exit 1
    }
}

# 检查 pnpm 是否安装
try {
    $null = Get-Command pnpm -ErrorAction Stop
} catch {
    Write-Host "pnpm 未安装，请先运行: npm install -g pnpm" -ForegroundColor Red
    exit 1
}

# 检查 next 是否可用（如果 node_modules 存在但 next 缺失，会导致 'next' 不是命令）
# 说明：这里不用多行括号数组字面量，避免某些终端/编码环境下解析到 ')' 时报错
# 用 ArrayList 避免某些环境下泛型 List 创建异常导致变量为 $null
$nextCmdCandidates = New-Object System.Collections.ArrayList
$nextCmdCandidates.Add((Join-Path $PROJECT_ROOT "frontend\web\node_modules\.bin\next.cmd")) | Out-Null
$nextCmdCandidates.Add((Join-Path $PROJECT_ROOT "frontend\node_modules\.bin\next.cmd")) | Out-Null
$nextCmdCandidates.Add((Join-Path $PROJECT_ROOT "frontend\web\node_modules\.bin\next")) | Out-Null
$nextCmdCandidates.Add((Join-Path $PROJECT_ROOT "frontend\node_modules\.bin\next")) | Out-Null

$nextCmd = $nextCmdCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $nextCmd) {
    Write-Host "未检测到 next，可执行文件缺失，尝试重新安装前端依赖..." -ForegroundColor Yellow
    Set-Location "$PROJECT_ROOT\frontend"
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pnpm install 失败，请先修复依赖安装问题" -ForegroundColor Red
        exit 1
    }

    $nextCmd = $nextCmdCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

    if (-not $nextCmd) {
        Write-Host "依赖已安装但仍找不到 next。请检查 frontend/web/package.json 是否包含 next 依赖，以及 pnpm 工作区是否正常。" -ForegroundColor Red
        exit 1
    }
}

# 启动 Web 应用
Write-Host "启动 Next.js Web 应用..." -ForegroundColor Green
Write-Host "访问地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

# 确保在 frontend 目录
Set-Location "$PROJECT_ROOT\frontend"

# 使用 pnpm --filter 运行（这是 pnpm workspace 的标准方式）
pnpm --filter web dev
