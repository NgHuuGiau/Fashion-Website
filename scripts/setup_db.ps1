# ============================================================
# Fashion Website - Full Database Setup Script
# Chạy từ ROOT REPO: .\scripts\setup_db.ps1
# ============================================================

param(
    [string]$Server = "localhost",
    [string]$Database = "HUUGIAU_Fashion",
    [switch]$SkipMigrate,
    [switch]$SkipDemoData,
    [switch]$SkipLegacyImport
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$demoSql = Join-Path $repoRoot "database\sql\02_DEMO_DATA.sql"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Fashion Website - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Server: $Server" -ForegroundColor Gray
Write-Host "Database: $Database" -ForegroundColor Gray
Write-Host ""

# Check prerequisites
if (-not (Test-Path $backendDir)) {
    throw "Không tìm thấy folder backend: $backendDir"
}
if (-not (Test-Path $demoSql) -and !$SkipDemoData) {
    throw "Không tìm thấy demo SQL: $demoSql"
}
if (-not (Get-Command sqlcmd.exe -ErrorAction SilentlyContinue) -and !$SkipDemoData) {
    Write-Warning "sqlcmd.exe không tìm thấy - sẽ bỏ qua load demo data"
    $SkipDemoData = $true
}

cd $backendDir

# 1. Django Migrate
if (!$SkipMigrate) {
    Write-Host "`n[1/3] Django Migrate..." -ForegroundColor Yellow
    python manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw "Migrate thất bại" }
    Write-Host "  -> Migrate OK" -ForegroundColor Green
}

# 2. Load Demo Data (via Django ORM)
if (!$SkipDemoData) {
    Write-Host "`n[2/3] Load Demo Data..." -ForegroundColor Yellow
    python manage.py seed_products --sync
    if ($LASTEXITCODE -ne 0) { throw "Sync products thất bại" }
    # Demo data already seeded via Django ORM
    # Nếu cần tạo lại: python seed_demo.py
    Write-Host "  -> Demo data OK (seeded via Django ORM)" -ForegroundColor Green
}

# 3. Import Legacy Data (optional)
if (!$SkipLegacyImport) {
    Write-Host "`n[3/3] Import Legacy Data..." -ForegroundColor Yellow
    python manage.py import_legacy --no-input
    if ($LASTEXITCODE -ne 0) { throw "Import legacy thất bại" }
    Write-Host "  -> Legacy import OK" -ForegroundColor Green
}

# Verify
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Verify Data" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
python -c "
import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'
import django; django.setup()
from django.contrib.auth.models import User
from orders.models import Coupon, Order, OrderItem
from products.models import Review
from users.models import UserAddress
print('Users:', User.objects.count())
print('Coupons:', __import__('orders.models', fromlist=['Coupon']).Coupon.objects.count())
print('Orders:', __import__('orders.models', fromlist=['Order']).Order.objects.count())
print('OrderItems:', __import__('orders.models', fromlist=['OrderItem']).OrderItem.objects.count())
print('Reviews:', __import__('products.models', fromlist=['Review']).Review.objects.count())
print('Addresses:', __import__('users.models', fromlist=['UserAddress']).UserAddress.objects.count())
"

Write-Host "`nDone!" -ForegroundColor Green