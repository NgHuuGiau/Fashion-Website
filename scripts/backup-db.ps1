param(
    [string]$Database = "HUUGIAU_Fashion",
    [string]$Server = ".",
    [string]$BackupDirectory = "..\backups\db"
)

$ErrorActionPreference = "Stop"
if ($Database -notmatch '^[A-Za-z0-9_-]+$') { throw "Invalid database name." }

$directory = [System.IO.Path]::GetFullPath($BackupDirectory)
New-Item -ItemType Directory -Path $directory -Force | Out-Null
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $directory "${Database}_${timestamp}.bak"
$sqlPath = $backupFile.Replace("'", "''")
$sql = @"
BACKUP DATABASE [$Database] TO DISK = N'$sqlPath' WITH COPY_ONLY, COMPRESSION, CHECKSUM, INIT;
RESTORE VERIFYONLY FROM DISK = N'$sqlPath' WITH CHECKSUM;
"@

& sqlcmd -S $Server -E -C -b -Q $sql
if ($LASTEXITCODE -ne 0) { throw "SQL Server backup or verification failed." }
Write-Host "Verified SQL Server backup: $backupFile"
