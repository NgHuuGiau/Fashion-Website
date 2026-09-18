$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$backendPath = Join-Path $repoRoot "backend"
$python = Join-Path $backendPath ".venv\Scripts\python.exe"
$waitress = Join-Path $backendPath ".venv\Scripts\waitress-serve.exe"
$productionEnv = Join-Path $repoRoot ".env.production"

if (-not (Test-Path -LiteralPath $productionEnv -PathType Leaf)) {
    throw "Missing $productionEnv. Create it from .env.production.example and fill verified values."
}
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Missing backend virtualenv. Create backend\.venv and install backend requirements first."
}
if (-not (Test-Path -LiteralPath $waitress -PathType Leaf)) {
    throw "Waitress is not installed in backend\.venv. Run: backend\.venv\Scripts\python.exe -m pip install waitress"
}

$env:APP_ENV_FILE = ".env.production"
$env:DJANGO_SETTINGS_MODULE = "core.settings"
Push-Location $backendPath
try {
    & $python manage.py check --deploy
    if ($LASTEXITCODE -ne 0) { throw "Django deploy check failed." }

    & $python manage.py compress --force
    if ($LASTEXITCODE -ne 0) { throw "Static asset compression failed." }

    & $python manage.py collectstatic --noinput
    if ($LASTEXITCODE -ne 0) { throw "Collectstatic failed." }

    & $waitress --listen=127.0.0.1:8000 --threads=8 core.wsgi:application
    if ($LASTEXITCODE -ne 0) { throw "Waitress stopped with an error." }
}
finally {
    Pop-Location
}
