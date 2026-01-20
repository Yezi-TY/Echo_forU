﻿﻿﻿# 启动桌面应用（Tauri）脚本 - PowerShell

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

Write-Host "启动桌面应用..." -ForegroundColor Green
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

# 检查 pnpm 是否安装
try {
    $null = Get-Command pnpm -ErrorAction Stop
} catch {
    Write-Host "pnpm 未安装，请先运行: npm install -g pnpm" -ForegroundColor Red
    exit 1
}

# 检查 Rust 是否安装（Tauri 需要）
try {
    $null = Get-Command cargo -ErrorAction Stop
} catch {
    Write-Host "Rust/Cargo 未安装，Tauri 需要 Rust 环境" -ForegroundColor Yellow
    Write-Host "安装方法: 访问 https://rustup.rs/" -ForegroundColor Yellow
    exit 1
}

# 启动桌面应用
Write-Host "启动 Tauri 桌面应用..." -ForegroundColor Green
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Gray
Write-Host ""

Set-Location "$PROJECT_ROOT\frontend"
pnpm --filter desktop tauri:dev

