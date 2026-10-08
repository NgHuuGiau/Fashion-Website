param(
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1",
    [switch]$NoBrowser,
    [switch]$Lan
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

# Mo cho may khac trong LAN: bind all interfaces + nhan IP LAN vao
# ALLOWED_HOSTS/CSRF (env process thang .env) + mo firewall.
if ($Lan) {
    $BindHost = "0.0.0.0"
    $lanIps = Get-NetIPAddress -AddressFamily IPv4 |
        Where-Object { $_.IPAddress -notmatch "^(127|169\.254)" } |
        Select-Object -ExpandProperty IPAddress | Sort-Object -Unique
    $env:ALLOWED_HOSTS = ((@("127.0.0.1", "localhost") + $lanIps) -join ",")
    $origins = @("http://localhost:${Port}", "http://127.0.0.1:${Port}") +
        ($lanIps | ForEach-Object { "http://${_}:${Port}" })
    $env:CSRF_TRUSTED_ORIGINS = ($origins -join ",")
    try {
        if (-not (Get-NetFirewallRule -DisplayName "HUUGIAU Fashion Web" -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -DisplayName "HUUGIAU Fashion Web" `
                -Direction Inbound -Protocol TCP -LocalPort $Port -Action Allow | Out-Null
            Write-Host "Da mo firewall port ${Port}." -ForegroundColor Green
        }
    } catch {
        Write-Host "Khong mo duoc firewall (can quyen admin). May khac co the khong vao duoc." -ForegroundColor Yellow
    }
    $url = "http://$($lanIps[0]):${Port}/"
    Write-Host "May khac mo: $url" -ForegroundColor Green
}

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
    -ArgumentList "manage.py", "runserver", "${BindHost}:${Port}" `
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
