#!/bin/bash
# Backup script for HUUGIAU Fashion Website
# Usage: ./scripts/backup.sh [full|db|media]

set -euo pipefail

# Configuration
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
DB_PORT="${DB_PORT:-5432}"
DATE=$(date +"%Y%m%d_%H%M%S")
PROJECT_NAME="fashion-website"
RETENTION_DAYS=30

# S3 Configuration (optional - set in env)
S3_BUCKET="${BACKUP_S3_BUCKET:-}"
AWS_REGION="${AWS_REGION:-us-east-1}"

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

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}/db"
mkdir -p "${BACKUP_DIR}/media"

# Function to backup database
backup_database() {
    if [[ "${DB_ENGINE:-postgres}" == "mssql" ]]; then
        log_error "Use scripts/backup-db.ps1 for SQL Server; SQL Server backups are native .bak files."
        return 1
    fi

    local backup_file="${BACKUP_DIR}/db/${PROJECT_NAME}_db_${DATE}.dump.gz"
    
    log_info "Starting database backup..."
    
    PGPASSWORD="${DB_PASSWORD:-}" pg_dump -h "${DB_HOST:?Set DB_HOST}" \
        -p "${DB_PORT}" -U "${DB_USER:?Set DB_USER}" \
        -d "${DB_NAME:?Set DB_NAME}" --no-owner --no-acl \
        --format=custom --compress=9 | gzip -9 > "${backup_file}"
    gzip -t "${backup_file}"
    
    log_info "Database backup completed: ${backup_file}"
}

# Function to backup media files
backup_media() {
    local backup_file="${BACKUP_DIR}/media/${PROJECT_NAME}_media_${DATE}.tar.gz"
    local media_path="${PROJECT_ROOT}/frontend/static/images"
    
    if [ ! -d "${media_path}" ]; then
        log_warn "Media path not found: ${media_path}"
        return
    fi
    
    log_info "Starting media backup..."
    
    tar -czf "${backup_file}" -C "$(dirname "${media_path}")" "$(basename "${media_path}")"
    
    log_info "Media backup completed: ${backup_file}"
}

# Function to upload to S3
upload_to_s3() {
    if [ -z "${S3_BUCKET}" ]; then
        log_warn "S3_BUCKET not set, skipping S3 upload"
        return
    fi
    
    log_info "Uploading backups to S3..."
    
    aws s3 cp "${BACKUP_DIR}" "s3://${S3_BUCKET}/${PROJECT_NAME}/" \
        --recursive \
        --region "${AWS_REGION}" \
        --storage-class STANDARD_IA
    
    log_info "S3 upload completed"
}

# Function to clean old backups
cleanup_old_backups() {
    log_info "Cleaning backups older than ${RETENTION_DAYS} days..."
    
    find "${BACKUP_DIR}" -type f -mtime +${RETENTION_DAYS} -delete
    
    log_info "Cleanup completed"
}

# Main backup function
main() {
    local backup_type="${1:-full}"
    
    log_info "Starting backup (type: ${backup_type})..."
    
    case "${backup_type}" in
        db)
            backup_database
            ;;
        media)
            backup_media
            ;;
        full)
            backup_database
            backup_media
            ;;
        *)
            log_error "Invalid backup type: ${backup_type}. Use: full, db, or media"
            exit 1
            ;;
    esac
    
    if [ -n "${S3_BUCKET}" ]; then
        upload_to_s3
    fi
    
    cleanup_old_backups
    
    log_info "Backup completed successfully!"
}

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Run main
main "$@"
