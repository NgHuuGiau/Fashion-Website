@echo off
set DJANGO_SETTINGS_MODULE=core.test_settings_sqlite
set SQLITE_TEST_DB=D:\Project\Fashion-Website\.tmp-e2e.sqlite3
set REDIS_URL=
set SHOP_BANK_ACCOUNT=
set VNPAY_TMN_CODE=
D:\Project\Fashion-Website\.venv\Scripts\python.exe backend/manage.py runserver 127.0.0.1:8000 --noreload
