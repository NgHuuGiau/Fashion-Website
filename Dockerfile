FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc curl unixodbc unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Chạy dưới user thường, không root (giảm thiệt hại nếu bị RCE).
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/ || exit 1

CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py compress --force && python manage.py collectstatic --noinput --clear && exec python run_local.py 0.0.0.0 8000"]