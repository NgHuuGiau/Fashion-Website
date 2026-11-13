# Staging local https://127.0.0.1:8443 — mô phỏng prod sau Caddy (TLS internal CA).
# Khởi động:  1) .\scripts\start-staging-web.ps1   (waitress 127.0.0.1:8002)
#              2) C:\caddy\caddy.exe run --config Caddyfile.staging --adapter caddyfile
# Dừng: Ctrl+C từng cửa sổ. File .env.staging KHÔNG commit.
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendPath = Join-Path $repoRoot "backend"
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$stagingEnv = Join-Path $repoRoot ".env.staging"

if (-not (Test-Path -LiteralPath $stagingEnv -PathType Leaf)) {
    throw "Missing $stagingEnv."
}

$env:APP_ENV_FILE = ".env.staging"
$env:DJANGO_SETTINGS_MODULE = "core.settings"
$env:BEHIND_PROXY = "True"
Push-Location $backendPath
try {
    & $python manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Django check failed." }

    # Tin proxy localhost (Caddy) để X-Forwarded-Proto tới Django;
    # thiếu trusted-proxy sẽ redirect-loop https->https sau proxy.
    & $python -c "import os; os.environ['BEHIND_PROXY']='True'; from django.core.wsgi import get_wsgi_application; from waitress import serve; serve(get_wsgi_application(), listen='127.0.0.1:8002', threads=8, trusted_proxy='127.0.0.1')"
    if ($LASTEXITCODE -ne 0) { throw "Waitress stopped with an error." }
}
finally {
    Pop-Location
}
