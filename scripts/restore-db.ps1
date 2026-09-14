param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [string]$Database = "HUUGIAU_Fashion",
    [string]$Server = ".",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $BackupFile).Path
if (-not $Force) {
    $answer = Read-Host "Restore $Database from $resolved and overwrite the current database? Type RESTORE"
    if ($answer -cne "RESTORE") { throw "Restore cancelled." }
}

$escapedFile = $resolved.Replace("'", "''")
$sql = @"
IF DB_ID(N'$Database') IS NOT NULL
BEGIN
    ALTER DATABASE [$Database] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
END;
RESTORE DATABASE [$Database] FROM DISK = N'$escapedFile' WITH REPLACE, RECOVERY;
ALTER DATABASE [$Database] SET MULTI_USER;
"@

& sqlcmd -S $Server -E -C -b -Q $sql
if ($LASTEXITCODE -ne 0) { throw "SQL Server restore failed." }
Write-Host "Database restored successfully: $Database"
