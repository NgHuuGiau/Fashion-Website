#!/bin/bash
# Restore script for HUUGIAU Fashion Website
# Usage: ./scripts/restore.sh [db|media] [backup_file]

set -e

# Configuration
BACKUP_DIR="/backups"
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
    
    log_warn "This will REPLACE the current database. Are you sure? (y/N)"
    read -r confirm
    if [[ ! "${confirm}" =~ ^[Yy]$ ]]; then
        log_info "Restore cancelled"
        exit 0
    fi
    
    log_info "Starting database restore from ${backup_file}..."
    
    if [[ "${backup_file}" == *.dump.gz ]] || [[ "${backup_file}" == *.dump ]]; then
        # PostgreSQL restore
        local dump_file="${backup_file}"
        if [[ "${backup_file}" == *.gz ]]; then
            gunzip -c "${backup_file}" > "${backup_file%.gz}"
            dump_file="${backup_file%.gz}"
        else
            dump_file="${backup_file}"
        fi
        
        pg_restore -h "${DB_HOST}" \
                   -p "${DB_PORT}" \
                   -U "${DB_USER}" \
                   -d "${DB_NAME}" \
                   --clean --if-exists --no-owner --no-acl \
                   "${dump_file}"
    elif [[ "${backup_file}" == *.sql.gz ]] || [[ "${backup_file}" == *.sql ]]; then
        # SQL Server restore
        local sql_file="${backup_file}"
        if [[ "${backup_file}" == *.gz ]]; then
            gunzip -c "${backup_file}" > "${backup_file%.gz}"
            sql_file="${backup_file%.gz}"
        else
            sql_file="${backup_file}"
        fi
        
        sqlcmd -S "${DB_HOST},${DB_PORT}" \
               -U "${DB_USER}" \
               -P "${DB_PASSWORD}" \
               -d "${DB_NAME}" \
               -i "${sql_file}"
    else
        log_error "Unsupported backup file format: ${backup_file}"
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
    
    local media_path="${PROJECT_ROOT}/backend/frontend/static/images"
    
    log_info "Restoring media from ${backup_file}..."
    
    # Backup current media first
    if [ -d "${media_path}" ]; then
        mv "${media_path}" "${media_path}.backup.$(date +%s)"
    fi
    
    mkdir -p "$(dirname "${media_path}")"
    tar -xzf "${backup_file}" -C "$(dirname "${media_path}")"
    
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

# Load environment variables
if [ -f "${PROJECT_ROOT}/.env" ]; then
    export $(grep -v '^#' "${PROJECT_ROOT}/.env" | xargs)
fi

PROJECT_ROOT="${PROJECT_ROOT:-$(dirname "$0")/..}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"

main "$@"