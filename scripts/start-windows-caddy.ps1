param(
    [Parameter(Mandatory = $true)]
    [string]$Domain,
    [Parameter(Mandatory = $true)]
    [string]$AcmeEmail,
    [Parameter(Mandatory = $true)]
    [string]$MediaRoot
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$caddyfile = Join-Path $repoRoot "Caddyfile.windows"
$staticRoot = Join-Path $repoRoot "backend\staticfiles"
$mediaPath = [System.IO.Path]::GetFullPath($MediaRoot)
$driveRoot = [System.IO.Path]::GetPathRoot($mediaPath)
$repoPrefix = $repoRoot.TrimEnd([char[]]@('\', '/')) + [System.IO.Path]::DirectorySeparatorChar

if ($mediaPath.TrimEnd([char[]]@('\', '/')) -eq $driveRoot.TrimEnd([char[]]@('\', '/'))) {
    throw "MEDIA_ROOT must be a dedicated folder, not a drive root."
}
if ($mediaPath.Equals($repoRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
    $mediaPath.StartsWith($repoPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "MEDIA_ROOT must be outside the repository so deployments cannot overwrite uploaded files."
}
if (-not (Get-Command caddy -ErrorAction SilentlyContinue)) {
    throw "Caddy is not installed or is not available on PATH."
}
if (-not (Test-Path -LiteralPath $staticRoot -PathType Container)) {
    throw "Static files are missing. Run scripts\start-windows-web.ps1 once to collect them."
}

New-Item -ItemType Directory -Path $mediaPath -Force | Out-Null
$env:DOMAIN = $Domain
$env:ACME_EMAIL = $AcmeEmail
$env:STATIC_ROOT = $staticRoot -replace '\\', '/'
$env:MEDIA_ROOT = $mediaPath -replace '\\', '/'

& caddy run --config $caddyfile --adapter caddyfile
if ($LASTEXITCODE -ne 0) { throw "Caddy stopped with an error." }
