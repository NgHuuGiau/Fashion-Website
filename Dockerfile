FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

WORKDIR /app

# pyodbc (mssql-django) cần unixodbc runtime; gcc cho build nếu wheel thiếu
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

WORKDIR /app/backend
EXPOSE 8000

# migrate → compress offline (bắt buộc khi DEBUG=False) → collectstatic → chạy ASGI
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py compress --force && python manage.py collectstatic --noinput --clear && exec python run_local.py 0.0.0.0 8000"]