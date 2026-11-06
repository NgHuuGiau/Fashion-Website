#!/usr/bin/env bash
# Restore PostgreSQL hoặc volume media từ backup của scripts/backup.sh.
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
kind="${1:-}"
file="${2:-}"

if [[ -z "$kind" || -z "$file" ]]; then
    echo "Usage: $0 db|media BACKUP_FILE"
    find "$backup_dir" -maxdepth 1 -type f \( -name 'db_*.dump' -o -name 'media_*.tar.gz' \) -print 2>/dev/null || true
    exit 1
fi
if [[ ! -f "$file" ]]; then
    echo "Backup not found: $file" >&2
    exit 1
fi

if [[ "$kind" == db ]]; then
    if [[ "$file" != *.dump && "$file" != *.dump.gz ]]; then
        echo "Expected a PostgreSQL .dump or .dump.gz file" >&2
        exit 1
    fi
    dump="$file"
    temp_dump=""
    if [[ "$file" == *.gz ]]; then
        temp_dump=$(mktemp)
        trap 'rm -f -- "$temp_dump"' EXIT
        gzip -dc "$file" > "$temp_dump"
        dump="$temp_dump"
    fi
    "${compose[@]}" exec -T db pg_restore --list < "$dump" > /dev/null
    echo "This replaces the PostgreSQL database configured in $COMPOSE_ENV_FILE. Type RESTORE to continue:"
    read -r confirm
    [[ "$confirm" == RESTORE ]] || exit 0
    "${compose[@]}" exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-acl' < "$dump"
elif [[ "$kind" == media ]]; then
    [[ "$file" == *.tar.gz ]] || { echo "Expected a .tar.gz media file" >&2; exit 1; }
    while IFS= read -r member; do
        if [[ "$member" == /* || "/$member/" == *"/../"* || ( "$member" != media && "$member" != media/* ) || "$member" == media/.restore-* ]]; then
            echo "Unsafe media archive path: $member" >&2
            exit 1
        fi
    done < <(tar -tzf "$file")
    tar -tzf "$file" > /dev/null
    if tar -tvzf "$file" | awk 'substr($0, 1, 1) !~ /^[-d]$/ { bad=1 } END { exit !bad }'; then
        echo "Media archive can contain only files and directories" >&2
        exit 1
    fi
    echo "This replaces the media volume and keeps the old files in .restore-backup. Type RESTORE to continue:"
    read -r confirm
    [[ "$confirm" == RESTORE ]] || exit 0
    "${compose[@]}" run --rm --no-deps --user root -T app sh -ec '
        stage=$(mktemp -d /app/media/.restore-stage.XXXXXX)
        trap '\''rm -rf -- "$stage"'\'' EXIT
        tar -xzf - -C "$stage" --strip-components=1 --no-same-owner
        backup="/app/media/.restore-backup.$(date +%s)"
        mkdir "$backup"
        find /app/media -mindepth 1 -maxdepth 1 ! -path "$stage" ! -path "$backup" -exec mv -t "$backup" -- {} +
        find "$stage" -mindepth 1 -maxdepth 1 -exec mv -t /app/media -- {} +
        chown -R 10001:10001 /app/media
    ' < "$file"
else
    echo "Expected db or media" >&2
    exit 1
fi
echo "Restore complete: $file"
