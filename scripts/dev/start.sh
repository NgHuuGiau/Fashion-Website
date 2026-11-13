#!/bin/bash
# Use WSL if available, or set env and run python
export DJANGO_SETTINGS_MODULE=core.test_settings_sqlite
export SQLITE_TEST_DB=/d/Project/Fashion-Website/.tmp-e2e.sqlite3
python backend/manage.py runserver 127.0.0.1:8000 --noreload
