param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Database = "HUUGIAU_Fashion",
    [string]$Server = ".",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $BackupFile).Path
if ([System.IO.Path]::GetExtension($resolved) -ne ".bak") {
    throw "Expected a native SQL Server .bak file."
}
if (-not $Force) {
    $answer = Read-Host "Restore $Database from $resolved and overwrite the current database? Type RESTORE"
    if ($answer -cne "RESTORE") { throw "Restore cancelled." }
}

$escapedFile = $resolved.Replace("'", "''")
$sql = @"
BEGIN TRY
    IF DB_ID(N'$Database') IS NOT NULL
    BEGIN
        ALTER DATABASE [$Database] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    END;

    RESTORE DATABASE [$Database] FROM DISK = N'$escapedFile' WITH REPLACE, RECOVERY;
    ALTER DATABASE [$Database] SET MULTI_USER;
END TRY
BEGIN CATCH
    BEGIN TRY
        IF DB_ID(N'$Database') IS NOT NULL
        BEGIN
            ALTER DATABASE [$Database] SET MULTI_USER;
        END;
    END TRY
    BEGIN CATCH
        -- Preserve the restore error; an administrator may need to reset access manually.
    END CATCH;

    THROW;
END CATCH;
"@

& sqlcmd -S $Server -E -C -b -Q $sql
if ($LASTEXITCODE -ne 0) { throw "SQL Server restore failed." }
Write-Host "Database restored successfully: $Database"
