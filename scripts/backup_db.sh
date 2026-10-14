#!/usr/bin/env bash
# Backup/Restore script for Fashion-Website PostgreSQL database
# Usage:
#   ./backup_db.sh backup [output_file]
#   ./backup_db.sh restore <input_file>
#   ./backup_db.sh list

set -euo pipefail

# Load env
if [[ -f ".env.production" ]]; then
    set -a
    source .env.production
    set +a
elif [[ -f ".env" ]]; then
    set -a
    source .env
    set +a
fi

DB_NAME="${DB_NAME:-huugiau_fashion}"
DB_USER="${DB_USER:-huugiau}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_PASSWORD="${DB_PASSWORD}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DEFAULT_OUTPUT="${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

command="${1:-}"
case "${command}" in
    backup)
        output_file="${2:-${DEFAULT_OUTPUT}}"
        echo "📦 Backing up ${DB_NAME} to ${output_file}..."
        PGPASSWORD="${DB_PASSWORD}" pg_dump \
            -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
            -d "${DB_NAME}" --no-owner --no-privileges \
            | gzip > "${output_file}"
        echo "✅ Backup complete: ${output_file}"
        ls -lh "${output_file}"
        ;;

    restore)
        input_file="${2:-}"
        if [[ -z "${input_file}" ]]; then
            echo "Usage: $0 restore <backup_file.sql.gz>"
            exit 1
        fi
        if [[ ! -f "${input_file}" ]]; then
            echo "❌ File not found: ${input_file}"
            exit 1
        fi
        echo "⚠️  Restoring ${DB_NAME} from ${input_file}..."
        echo "This will DESTROY existing data. Continue? (y/N)"
        read -r confirm
        if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
            echo "Aborted."
            exit 1
        fi
        # Terminate existing connections
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
            -d postgres -c "
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '${DB_NAME}' AND pid <> pg_backend_pid();"
        # Drop & recreate
        PGPASSWORD="${DB_PASSWORD}" psql \
            -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
            -d postgres -c "DROP DATABASE IF EXISTS ${DB_NAME}; CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
        # Restore
        gunzip -c "${input_file}" | PGPASSWORD="${DB_PASSWORD}" psql \
            -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" \
            -d "${DB_NAME}" -q
        echo "✅ Restore complete"
        ;;

    list)
        echo "📋 Available backups in ${BACKUP_DIR}:"
        ls -lh "${BACKUP_DIR}"/*.sql.gz 2>/dev/null || echo "No backups found"
        ;;

    *)
        echo "Usage: $0 {backup|restore|list} [file]"
        echo "  backup [output_file]  - Create compressed backup (default: backups/db_TIMESTAMP.sql.gz)"
        echo "  restore <input_file>  - Restore from compressed backup"
        echo "  list                  - List available backups"
        exit 1
        ;;
esac