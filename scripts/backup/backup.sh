#!/usr/bin/env bash
# Sao lưu PostgreSQL và volume media của Docker Compose production.
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
COMPOSE_ENV_FILE="${COMPOSE_ENV_FILE:-.env.compose.production}"
cd "$APP_DIR"
if [[ ! -f "$COMPOSE_ENV_FILE" ]]; then
    echo "Missing $COMPOSE_ENV_FILE" >&2
    exit 1
fi

compose=(docker compose --env-file "$COMPOSE_ENV_FILE" -f docker-compose.yml -f docker-compose.production.yml)
backup_dir="$APP_DIR/backups"
stamp=$(date +%Y%m%d_%H%M%S)
mkdir -p "$backup_dir"
chmod 700 "$backup_dir"
db_file="$backup_dir/db_$stamp.dump"
media_file="$backup_dir/media_$stamp.tar.gz"
trap 'rm -f -- "$db_file.tmp" "$media_file.tmp"' EXIT

"${compose[@]}" exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --no-owner --no-acl' > "$db_file.tmp"
"${compose[@]}" exec -T db pg_restore --list < "$db_file.tmp" > /dev/null
mv -- "$db_file.tmp" "$db_file"

"${compose[@]}" exec -T app tar -C /app --exclude='media/.restore-backup.*' --exclude='media/.restore-stage.*' -czf - media > "$media_file.tmp"
tar -tzf "$media_file.tmp" > /dev/null
mv -- "$media_file.tmp" "$media_file"

find "$backup_dir" -maxdepth 1 -type f \( -name 'db_*.dump' -o -name 'media_*.tar.gz' \) -mtime +30 -delete
echo "Backup complete: $db_file, $media_file"
