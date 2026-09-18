#!/bin/bash
# Restore script for HUUGIAU Fashion Website
# Usage: ./scripts/restore.sh [db|media] [backup_file]

set -euo pipefail

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
DB_PORT="${DB_PORT:-5432}"
PROJECT_NAME="fashion-website"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to restore database
restore_database() {
    local backup_file="$1"
    
    if [ ! -f "${backup_file}" ]; then
        log_error "Backup file not found: ${backup_file}"
        exit 1
    fi
    
    if [[ "${DB_ENGINE:-postgres}" == "mssql" ]]; then
        log_error "Use scripts/restore-db.ps1 to restore a SQL Server .bak file."
        exit 1
    fi

    log_warn "This replaces database ${DB_NAME:?Set DB_NAME}. Type RESTORE to continue:"
    read -r confirm
    if [[ "${confirm}" != "RESTORE" ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    log_info "Starting database restore from ${backup_file}..."
    
    if [[ "${backup_file}" == *.dump.gz ]] || [[ "${backup_file}" == *.dump ]]; then
        # PostgreSQL restore
        local dump_file="${backup_file}"
        local temp_dump=""
        if [[ "${backup_file}" == *.gz ]]; then
            temp_dump=$(mktemp)
            gunzip -c "${backup_file}" > "${temp_dump}"
            dump_file="${temp_dump}"
        fi
        if ! pg_restore --list "${dump_file}" >/dev/null; then
            if [[ -n "${temp_dump}" ]]; then rm -f -- "${temp_dump}"; fi
            log_error "Backup archive is invalid."
            exit 1
        fi
        PGPASSWORD="${DB_PASSWORD:-}" pg_restore -h "${DB_HOST:?Set DB_HOST}" \
            -p "${DB_PORT}" -U "${DB_USER:?Set DB_USER}" \
            -d "${DB_NAME}" --clean --if-exists --no-owner --no-acl \
            "${dump_file}"
        if [[ -n "${temp_dump}" ]]; then rm -f -- "${temp_dump}"; fi
    else
        log_error "Expected a PostgreSQL .dump/.dump.gz backup; SQL Server requires a .bak file and restore-db.ps1."
        exit 1
    fi
    
    log_info "Database restore completed successfully!"
}

# Function to restore media
restore_media() {
    local backup_file="$1"
    
    if [ ! -f "${backup_file}" ]; then
        log_error "Backup file not found: ${backup_file}"
        exit 1
    fi
    
    log_warn "This will REPLACE current media files. Are you sure? (y/N)"
    read -r confirm
    if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    local media_path="${PROJECT_ROOT}/frontend/static/images"
    local staging_dir
    staging_dir=$(mktemp -d)

    while IFS= read -r member; do
        if [[ "${member}" == /* || "${member}" == *"../"* || ( "${member}" != "images" && "${member}" != images/* ) ]]; then
            rmdir "${staging_dir}"
            log_error "Unsafe or unexpected path in media archive: ${member}"
            exit 1
        fi
    done < <(tar -tzf "${backup_file}")
    
    log_info "Restoring media from ${backup_file}..."
    
    tar -xzf "${backup_file}" -C "${staging_dir}"

    # Keep current media recoverable before replacing it.
    if [ -d "${media_path}" ]; then
        mv "${media_path}" "${media_path}.backup.$(date +%s)"
    fi

    mkdir -p "$(dirname "${media_path}")"
    mv "${staging_dir}/images" "${media_path}"
    rmdir "${staging_dir}"
    
    log_info "Media restore completed successfully!"
}

# Main restore function
main() {
    local restore_type="${1:-db}"
    local backup_file="${2:-}"
    
    if [ -z "${backup_file}" ]; then
        # List available backups
        log_info "Available database backups:"
        ls -lh "${BACKUP_DIR}/db/" 2>/dev/null || log_warn "No database backups found"
        
        log_info "Available media backups:"
        ls -lh "${BACKUP_DIR}/media/" 2>/dev/null || log_warn "No media backups found"
        exit 0
    fi
    
    case "${restore_type}" in
        db)
            restore_database "${backup_file}"
            ;;
        media)
            restore_media "${backup_file}"
            ;;
        *)
            log_error "Invalid restore type: ${restore_type}. Use: db or media"
            exit 1
            ;;
    esac
    
    log_info "Restore completed successfully!"
}

main "$@"
