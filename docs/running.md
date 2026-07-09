# Running

## Fastest way

```powershell
.\scripts\run_local.ps1
```

That script:

1. checks Django settings
2. runs migrations
3. seeds sample products
4. opens the browser at `http://localhost:8000/`
5. starts the local server

## Options

```powershell
.\scripts\run_local.ps1 -SkipMigrate
.\scripts\run_local.ps1 -SkipSeed
.\scripts\run_local.ps1 -Port 9000
.\scripts\run_local.ps1 -BindHost 127.0.0.1
```

## Manual run

```powershell
.venv\Scripts\Activate.ps1
cd backend
python manage.py check
python manage.py migrate
python manage.py seed_products --sync
python manage.py runserver localhost:8000
```

## Important URLs

- Home: `http://localhost:8000/`
- Login: `http://localhost:8000/dang-nhap/`
- Register: `http://localhost:8000/dang-ky/`
- Cart: `http://localhost:8000/gio-hang/`
- Checkout: `http://localhost:8000/thanh-toan/`
- Shop admin dashboard: `http://localhost:8000/admin-dashboard/`

## Smoke test

```powershell
.\scripts\local_smoke_test.ps1
```

It checks:

- Django import
- `manage.py check`
- migrations
- product seeding
- server responds with HTTP 200
