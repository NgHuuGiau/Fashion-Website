<#
.SYNOPSIS
    Backup/Restore script for Fashion-Website PostgreSQL database (PowerShell 5.1 compatible)

.DESCRIPTION
    Usage:
        .\backup_db.ps1 backup [output_file]
        .\backup_db.ps1 restore <input_file>
        .\backup_db.ps1 list

    Requires: pg_dump, pg_restore, psql, gzip in PATH
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('backup','restore','list')]
    [string]$Command,

    [Parameter(Position=1)]
    [string]$FilePath
)

# Load env
if (Test-Path ".env.production") {
    Get-Content .env.production | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"',"'")
            if (-not [string]::IsNullOrEmpty($key) -and -not [Environment]::GetEnvironmentVariable($key)) {
                [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            }
        }
    }
} elseif (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.*)') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim().Trim('"',"'")
            if (-not [string]::IsNullOrEmpty($key) -and -not [Environment]::GetEnvironmentVariable($key)) {
                [Environment]::SetEnvironmentVariable($key, $value, 'Process')
            }
        }
    }
}

function Get-EnvOrDefault([string]$Name, [string]$Default) {
    $val = [Environment]::GetEnvironmentVariable($Name, 'Process')
    if ([string]::IsNullOrEmpty($val)) { return $Default }
    return $val
}

$DB_NAME = Get-EnvOrDefault 'DB_NAME' 'huugiau_fashion'
$DB_USER = Get-EnvOrDefault 'DB_USER' 'huugiau'
$DB_HOST = Get-EnvOrDefault 'DB_HOST' 'localhost'
$DB_PORT = Get-EnvOrDefault 'DB_PORT' '5432'
$DB_PASSWORD = Get-EnvOrDefault 'DB_PASSWORD' ''
$BACKUP_DIR = Get-EnvOrDefault 'BACKUP_DIR' '.\backups'
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$DEFAULT_OUTPUT = Join-Path $BACKUP_DIR ("{0}_{1}.sql.gz" -f $DB_NAME, $TIMESTAMP)

if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

switch ($Command) {
    'backup' {
        $output = if ($FilePath) { $FilePath } else { $DEFAULT_OUTPUT }
        Write-Host "Backing up $DB_NAME to $output..." -ForegroundColor Cyan
        $env:PGPASSWORD = $DB_PASSWORD
        pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --no-owner --no-privileges | gzip > $output
        Write-Host "Backup complete: $output" -ForegroundColor Green
        Get-Item $output | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
    }

    'restore' {
        if (-not $FilePath) {
            Write-Host "Usage: .\backup_db.ps1 restore <backup_file.sql.gz>" -ForegroundColor Red
            exit 1
        }
        if (-not (Test-Path $FilePath)) {
            Write-Host "File not found: $FilePath" -ForegroundColor Red
            exit 1
        }
        Write-Host "Restoring $DB_NAME from $FilePath..." -ForegroundColor Yellow
        Write-Host "This will DESTROY existing data. Continue? (y/N)"
        $confirm = Read-Host
        if ($confirm -ne 'y' -and $confirm -ne 'Y') {
            Write-Host "Aborted." -ForegroundColor Gray
            exit 1
        }

        $env:PGPASSWORD = $DB_PASSWORD
        # Terminate existing connections
        $sql1 = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c $sql1

        # Drop & recreate
        $sql2 = "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c $sql2

        # Restore
        gzip -dc $FilePath | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -q
        Write-Host "Restore complete" -ForegroundColor Green
    }

    'list' {
        Write-Host "Available backups in ${BACKUP_DIR}:" -ForegroundColor Cyan
        Get-ChildItem "${BACKUP_DIR}\*.sql.gz" -ErrorAction SilentlyContinue |
            Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
    }

    default {
        Write-Host "Usage: .\backup_db.ps1 {backup|restore|list} [file]"
        Write-Host "  backup [output_file]  - Create compressed backup"
        Write-Host "  restore <input_file>  - Restore from compressed backup"
        Write-Host "  list                  - List available backups"
        exit 1
    }
}