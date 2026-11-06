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

function Test-TcpPortFree {
    param([int]$Port)
    $client = New-Object Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if ($iar.AsyncWaitHandle.WaitOne(400) -and $client.Connected) { return $false }
        return $true
    } catch { return $true }
    finally { $client.Close() }
}

function Get-HttpStatusFast {
    param([string]$Url)
    try { return (& curl.exe -k -s -o NUL -w "%{http_code}" $Url 2>$null) } catch { return "" }
}

function Get-PortOwnerPid {
    param([int]$Port)
    try {
        $conn = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($conn) { return $conn.OwningProcess }
    } catch { }
    return $null
}

# Port 8000 hay bi tien trinh runserver cu giu (Windows bao EACCES
# thay vi "already in use"). Co app san thi dung lai, khong thi doi port.
$SelectedPort = $null
foreach ($candidate in @($Port, 8001, 8080, 5000)) {
    if (Test-TcpPortFree $candidate) { $SelectedPort = $candidate; break }
    if ((Get-HttpStatusFast "http://127.0.0.1:$candidate/") -eq "200") {
        Write-Host "Port $candidate da co server dang chay - dung lai, khong khoi dong them." -ForegroundColor Yellow
        if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$candidate/" }
        exit 0
    }
}
if (-not $SelectedPort) {
    $owner = Get-PortOwnerPid $Port
    $hint = if ($owner) { " (PID $owner dang giu port - tat tien trinh cu roi chay lai)" } else { "" }
    throw "Port $Port dang ban$hint."
}
if ($SelectedPort -ne $Port) {
    Write-Host "Port $Port ban - tu doi sang $SelectedPort." -ForegroundColor Yellow
    $Port = $SelectedPort
}
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
