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
    throw "Không tìm thấy Python trong `.venv`: $pythonExe"
}

try {
    Step "Kiểm tra Django"
    & $pythonExe -c "import django; print(django.get_version())"

    Step "Kiểm tra cấu hình"
    Push-Location $backendDir
    & $pythonExe manage.py check

    Step "Chạy migrate"
    & $pythonExe manage.py migrate

    Step "Đồng bộ sản phẩm"
    & $pythonExe manage.py seed_products --sync

    Step "Bật server tạm trên cổng 8010"
    $serverProcess = Start-Process -FilePath $pythonExe -ArgumentList "manage.py","runserver","127.0.0.1:8010","--noreload" -WorkingDirectory $backendDir -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 4

    Step "Kiểm tra HTTP"
    $response = Invoke-WebRequest -Uri $testUrl -UseBasicParsing
    Write-Host "StatusCode: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "URL: $testUrl"

    if ($response.StatusCode -ne 200) {
        throw "Trang web không trả về 200 OK"
    }

    Write-Host ""
    Write-Host "KẾT LUẬN: Backend chạy được và trang chủ trả về HTTP 200." -ForegroundColor Green
    Write-Host "Nếu trình duyệt vẫn lỗi, nguyên nhân thường nằm ở browser đang ép HTTPS." -ForegroundColor Yellow
}
finally {
    Pop-Location
    if ($null -ne $serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force
    }
}
