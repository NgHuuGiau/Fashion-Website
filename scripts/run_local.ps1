param(
    [switch]$SkipMigrate,
    [switch]$SkipSeed,
    [switch]$SkipImport,
    [int]$Port = 8000,
    [string]$BindHost = "localhost"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:DEBUG = "True"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
if ($BindHost -eq "localhost") { $BindHost = "[::1]" }
$bind = "${BindHost}:$Port"
$openUrl = "https://localhost:$Port/"

function Step($message) {
    Write-Host ""
    Write-Host "== $message ==" -ForegroundColor Cyan
}

if (-not (Test-Path $pythonExe)) {
    throw "Không tìm thấy Python trong `.venv`: $pythonExe"
}

Push-Location $backendDir
try {
    Step "Kiểm tra cấu hình"
    & $pythonExe manage.py check

    if (-not $SkipMigrate) {
        Step "Chạy migrate"
        & $pythonExe manage.py migrate
    }

    if (-not $SkipImport) {
        Step "Import dữ liệu từ database/sql"
        & $pythonExe manage.py import_legacy
    }

    if (-not $SkipSeed) {
        Step "Đồng bộ sản phẩm"
        & $pythonExe manage.py seed_products --sync
    }

    Step "Bật server local (HTTPS)"
    Write-Host "Mở: $openUrl" -ForegroundColor Green
    Start-Process $openUrl
    & $pythonExe manage.py runserver $bind
}
finally {
    Pop-Location
}
