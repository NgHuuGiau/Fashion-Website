Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$testUrl = "http://127.0.0.1:8010/"
$serverProcess = $null

function Step($message) {
    Write-Host ""
    Write-Host "== $message ==" -ForegroundColor Cyan
}

if (-not (Test-Path $pythonExe)) {
    throw "Khong tim thay Python trong .venv: $pythonExe"
}

try {
    Step "Kiem tra Django"
    & $pythonExe -c "import django; print(django.get_version())"

    Step "Kiem tra cau hinh"
    Push-Location $backendDir
    & $pythonExe manage.py check

    Step "Chay migrate"
    & $pythonExe manage.py migrate

    Step "Dong bo san pham"
    & $pythonExe manage.py seed_products --sync

    Step "Bat server tam tren cong 8010"
    $serverProcess = Start-Process -FilePath $pythonExe -ArgumentList "manage.py","runserver","127.0.0.1:8010","--noreload" -WorkingDirectory $backendDir -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 4

    Step "Test HTTP"
    $response = Invoke-WebRequest -Uri $testUrl -UseBasicParsing
    Write-Host "StatusCode: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "URL: $testUrl"

    if ($response.StatusCode -ne 200) {
        throw "Trang web khong tra ve 200 OK"
    }

    Write-Host ""
    Write-Host "KET LUAN: Backend chay duoc va trang chu tra ve HTTP 200." -ForegroundColor Green
    Write-Host "Neu trinh duyet van loi, nguyen nhan nam o browser dang ep HTTPS." -ForegroundColor Yellow
}
finally {
    Pop-Location
    if ($null -ne $serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force
    }
}
