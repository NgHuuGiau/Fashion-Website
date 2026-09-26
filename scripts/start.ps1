param(
    [int]$Port = 8000,
    [string]$BindHost = "localhost",
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
# Chay local luon dung .env (DEBUG=True). Xoa APP_ENV_FILE/DEBUG lan tu terminal
# truoc do, keo keo theo env production gay crash SECRET_KEY nhu da gap.
Remove-Item Env:APP_ENV_FILE -ErrorAction SilentlyContinue
Remove-Item Env:DEBUG -ErrorAction SilentlyContinue
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$url = "http://${BindHost}:${Port}/"

if (-not (Test-Path $pythonExe)) {
    throw "Không tìm thấy Python trong `.venv`: $pythonExe"
}
if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
    throw "Cần curl.exe (có sẵn trên Windows 10+)."
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  HUUGIAU Fashion - Local HTTP Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Green
Write-Host ""

$proc = Start-Process -FilePath $pythonExe `
    -ArgumentList "manage.py", "runserver", "[::1]:${Port}" `
    -WorkingDirectory $backendDir -NoNewWindow -PassThru

$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    Start-Sleep -Milliseconds 500
    if ($proc.HasExited) { break }
    try {
        $code = & curl.exe -k -s -o NUL -w "%{http_code}" "$url" 2>$null
        if ($code -eq "200") { $ready = $true; break }
    } catch { }
}

if ($ready) {
    Write-Host "Server đã sẵn sàng." -ForegroundColor Green
    if (-not $NoBrowser) {
        Start-Process $url
    }
} else {
    if ($proc.HasExited) {
        Write-Host "Server thoát bất thường. Xem lỗi phía trên." -ForegroundColor Red
    } else {
        Write-Host "Server không phản hồi đúng hạn. Mở thủ công: $url" -ForegroundColor Yellow
    }
}

$proc.WaitForExit()
