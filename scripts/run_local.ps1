param(
    [switch]$SkipMigrate,
    [switch]$SkipSeed,
    [int]$Port = 8000,
    [string]$BindHost = "localhost"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$bind = "${BindHost}:$Port"
$openUrl = "http://localhost:$Port/"

function Step($message) {
    Write-Host ""
    Write-Host "== $message ==" -ForegroundColor Cyan
}

if (-not (Test-Path $pythonExe)) {
    throw "Khong tim thay Python trong .venv: $pythonExe"
}

Push-Location $backendDir
try {
    Step "Kiem tra cau hinh"
    & $pythonExe manage.py check

    if (-not $SkipMigrate) {
        Step "Chay migrate"
        & $pythonExe manage.py migrate
    }

    if (-not $SkipSeed) {
        Step "Dong bo san pham"
        & $pythonExe manage.py seed_products --sync
    }

    Step "Bat server local"
    Write-Host "Mo: $openUrl" -ForegroundColor Green
    Start-Process $openUrl
    & $pythonExe manage.py runserver $bind
}
finally {
    Pop-Location
}
