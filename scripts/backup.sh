#!/bin/bash
# backup.sh - Backup database và media

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/fashion-website}"
BACKUP_DIR="$APP_DIR/backups"
DATE=$(date +%F_%H-%M-%S)

mkdir -p "$BACKUP_DIR"

cd "$APP_DIR"

# Load env
if [ -f .env.production ]; then
    export $(grep -v '^#' .env.production | xargs)
fi

echo "=== Backup $DATE ==="

# 1. Database backup
echo "Backing up database..."
if docker compose -f docker-compose.yml -f docker-compose.production.yml ps db | grep -q "Up"; then
    docker compose -f docker-compose.yml -f docker-compose.production.yml exec -T db \
        pg_dump -U "${DB_USER:-huugiau}" "${DB_NAME:-huugiau_fashion}" | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"
    echo "  -> $BACKUP_DIR/db_$DATE.sql.gz"
else
    echo "  ⚠️ Database container not running"
fi

# 2. Media backup
echo "Backing up media..."
if [ -d "frontend/static/images" ]; then
    tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" frontend/static/images
    echo "  -> $BACKUP_DIR/media_$DATE.tar.gz"
else
    echo "  ⚠️ Media directory not found"
fi

# 3. Cleanup old backups (keep 30 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -type f -name "db_*.sql.gz" -mtime +30 -delete
find "$BACKUP_DIR" -type f -name "media_*.tar.gz" -mtime +30 -delete

echo "=== Backup completed ==="
ls -lh "$BACKUP_DIR"