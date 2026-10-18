<#
.SYNOPSIS
    Backup/Restore script for Fashion-Website database (PostgreSQL + SQL Server)

.DESCRIPTION
    Usage:
        .\backup_db.ps1 backup [-Engine PostgreSQL|SQLServer] [output_file]
        .\backup_db.ps1 restore [-Engine PostgreSQL|SQLServer] <input_file>
        .\backup_db.ps1 list [-Engine PostgreSQL|SQLServer]

    PostgreSQL requires: pg_dump, pg_restore, psql, gzip in PATH
    SQL Server requires: sqlcmd in PATH
#>

param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet('backup','restore','list')]
    [string]$Command,

    [Parameter(Position=1)]
    [ValidateSet('PostgreSQL','SQLServer')]
    [string]$Engine = 'PostgreSQL',

    [Parameter(Position=2)]
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

# Common settings
$DB_NAME = Get-EnvOrDefault 'DB_NAME' 'huugiau_fashion'
$BACKUP_DIR = Get-EnvOrDefault 'BACKUP_DIR' '.\backups'
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"

if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR | Out-Null
}

# PostgreSQL specific
if ($Engine -eq 'PostgreSQL') {
    $DB_USER = Get-EnvOrDefault 'DB_USER' 'huugiau'
    $DB_HOST = Get-EnvOrDefault 'DB_HOST' 'localhost'
    $DB_PORT = Get-EnvOrDefault 'DB_PORT' '5432'
    $DB_PASSWORD = Get-EnvOrDefault 'DB_PASSWORD' ''
    $DEFAULT_OUTPUT = Join-Path $BACKUP_DIR ("{0}_{1}.sql.gz" -f $DB_NAME, $TIMESTAMP)
}
# SQL Server specific
elseif ($Engine -eq 'SQLServer') {
    $DB_SERVER = Get-EnvOrDefault 'DB_SERVER' '.'
    $DEFAULT_OUTPUT = Join-Path $BACKUP_DIR ("{0}_{1}.bak" -f $DB_NAME, $TIMESTAMP)
}

switch ($Command) {
    'backup' {
        if ($Engine -eq 'PostgreSQL') {
            $output = if ($FilePath) { $FilePath } else { $DEFAULT_OUTPUT }
            Write-Host "Backing up PostgreSQL $DB_NAME to $output..." -ForegroundColor Cyan
            $env:PGPASSWORD = $DB_PASSWORD
            pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME --no-owner --no-privileges | gzip > $output
            Write-Host "Backup complete: $output" -ForegroundColor Green
            Get-Item $output | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
        }
        elseif ($Engine -eq 'SQLServer') {
            $output = if ($FilePath) { $FilePath } else { $DEFAULT_OUTPUT }
            Write-Host "Backing up SQL Server $DB_NAME to $output..." -ForegroundColor Cyan
            $sql = @"
BACKUP DATABASE [$DB_NAME] TO DISK = N'$output' WITH COPY_ONLY, COMPRESSION, CHECKSUM, INIT;
RESTORE VERIFYONLY FROM DISK = N'$output' WITH CHECKSUM;
"@
            & sqlcmd -S $DB_SERVER -E -C -b -Q $sql
            if ($LASTEXITCODE -ne 0) { throw "SQL Server backup or verification failed." }
            Write-Host "Verified SQL Server backup: $output" -ForegroundColor Green
            Get-Item $output | Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
        }
    }

    'restore' {
        if (-not $FilePath) {
            Write-Host "Usage: .\backup_db.ps1 restore [-Engine PostgreSQL|SQLServer] <input_file>" -ForegroundColor Red
            exit 1
        }
        if (-not (Test-Path $FilePath)) {
            Write-Host "File not found: $FilePath" -ForegroundColor Red
            exit 1
        }

        if ($Engine -eq 'PostgreSQL') {
            Write-Host "Restoring PostgreSQL $DB_NAME from $FilePath..." -ForegroundColor Yellow
            Write-Host "This will DESTROY existing data. Continue? (y/N)"
            $confirm = Read-Host
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "Aborted." -ForegroundColor Gray
                exit 1
            }
            $env:PGPASSWORD = $DB_PASSWORD
            $sql1 = "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c $sql1
            $sql2 = "DROP DATABASE IF EXISTS $DB_NAME; CREATE DATABASE $DB_NAME OWNER $DB_USER;"
            psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c $sql2
            gzip -dc $FilePath | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -q
            Write-Host "Restore complete" -ForegroundColor Green
        }
        elseif ($Engine -eq 'SQLServer') {
            Write-Host "Restoring SQL Server $DB_NAME from $FilePath..." -ForegroundColor Yellow
            Write-Host "This will DESTROY existing data. Continue? (y/N)"
            $confirm = Read-Host
            if ($confirm -ne 'y' -and $confirm -ne 'Y') {
                Write-Host "Aborted." -ForegroundColor Gray
                exit 1
            }
            $resolved = (Resolve-Path -LiteralPath $FilePath).Path
            if ([System.IO.Path]::GetExtension($resolved) -ne ".bak") {
                throw "Expected a native SQL Server .bak file."
            }
            $escapedFile = $resolved.Replace("'", "''")
            $sql = @"
BEGIN TRY
    IF DB_ID(N'$DB_NAME') IS NOT NULL
    BEGIN
        ALTER DATABASE [$DB_NAME] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    END;
    RESTORE DATABASE [$DB_NAME] FROM DISK = N'$escapedFile' WITH REPLACE, RECOVERY;
    ALTER DATABASE [$DB_NAME] SET MULTI_USER;
END TRY
BEGIN CATCH
    BEGIN TRY
        IF DB_ID(N'$DB_NAME') IS NOT NULL
        BEGIN
            ALTER DATABASE [$DB_NAME] SET MULTI_USER;
        END;
    END TRY;
    THROW;
END CATCH
"@
            & sqlcmd -S $DB_SERVER -E -C -b -Q $sql
            if ($LASTEXITCODE -ne 0) { throw "SQL Server restore failed." }
            Write-Host "Database restored successfully: $DB_NAME" -ForegroundColor Green
        }
    }

    'list' {
        if ($Engine -eq 'PostgreSQL') {
            $pattern = "*.sql.gz"
        }
        else {
            $pattern = "*.bak"
        }
        Write-Host "Available backups in ${BACKUP_DIR}:" -ForegroundColor Cyan
        Get-ChildItem "${BACKUP_DIR}\$pattern" -ErrorAction SilentlyContinue |
            Select-Object Name, Length, LastWriteTime | Format-Table -AutoSize
    }

    default {
        Write-Host "Usage: .\backup_db.ps1 {backup|restore|list} [-Engine PostgreSQL|SQLServer] [file]"
        Write-Host "  backup [output_file]    - Create compressed backup"
        Write-Host "  restore <input_file>    - Restore from compressed backup"
        Write-Host "  list                    - List available backups"
        exit 1
    }
}