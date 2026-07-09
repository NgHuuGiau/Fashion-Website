# Installation

## Requirements

- Windows 11+
- Python 3.10+
- PowerShell 7+

## Quick setup

```powershell
git clone <repo-url>
cd Fashion-Website
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Environment file

Create a `.env` file in the repo root if you want to override defaults:

```env
SECRET_KEY=django-insecure-change-this-in-env
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
DB_PATH=
```

## Notes

- SQLite data lives in `database/db.sqlite3`
- Static files live in `frontend/static`
- That folder also acts as the project `MEDIA_ROOT`
