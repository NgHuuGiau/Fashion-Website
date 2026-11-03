param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$Database = "HUUGIAU_Fashion",
    [string]$Server = ".",
    # Đặt tên database đích khác (diễn tập restore) — bắt buộc MOVE file.
    [ValidatePattern('^[A-Za-z0-9_-]+$')]
    [string]$RestoreAs = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$resolved = (Resolve-Path -LiteralPath $BackupFile).Path
if ([System.IO.Path]::GetExtension($resolved) -ne ".bak") {
    throw "Expected a native SQL Server .bak file."
}
$target = if ($RestoreAs) { $RestoreAs } else { $Database }
if (-not $Force) {
    $answer = Read-Host "Restore $target from $resolved and overwrite the current database? Type RESTORE"
    if ($answer -cne "RESTORE") { throw "Restore cancelled." }
}

$escapedFile = $resolved.Replace("'", "''")
$restoreOptions = "REPLACE, RECOVERY"

if ($RestoreAs) {
    $paths = & sqlcmd -S $Server -E -C -b -h -1 -W -Q "SET NOCOUNT ON; SELECT CONVERT(nvarchar(400), SERVERPROPERTY('InstanceDefaultDataPath')) + '|' + CONVERT(nvarchar(400), SERVERPROPERTY('InstanceDefaultLogPath'));"
    $pathLine = ($paths | Where-Object { $_ -match '\|' } | Select-Object -First 1)
    if (-not $pathLine) { throw "Cannot read SQL Server default data/log path." }
    $pathParts = $pathLine -split '\|'
    $dataDir = $pathParts[0].Trim()
    $logDir = $pathParts[1].Trim()

    $fileRows = & sqlcmd -S $Server -E -C -b -h -1 -W -s "|" -Q "SET NOCOUNT ON; RESTORE FILELISTONLY FROM DISK = N'$escapedFile';"
    $moves = foreach ($row in $fileRows) {
        $parts = "$row" -split '\|'
        if ($parts.Count -lt 3) { continue }
        $logical = $parts[0].Trim()
        $isLog = $parts[2].Trim() -eq "L"
        $dir = if ($isLog) { $logDir } else { $dataDir }
        $ext = if ($isLog) { "ldf" } else { "mdf" }
        $safeName = ($logical -replace '[^A-Za-z0-9_]', '_')
        $targetPath = Join-Path $dir ("{0}_{1}.{2}" -f $target, $safeName, $ext)
        "MOVE N'{0}' TO N'{1}'" -f ($logical -replace "'", "''"), ($targetPath -replace "'", "''")
    }
    if (-not $moves) { throw "RESTORE FILELISTONLY returned no files; check the backup file." }
    $restoreOptions = $restoreOptions + ", " + ($moves -join ", ")
}

$sql = @"
BEGIN TRY
    IF DB_ID(N'$target') IS NOT NULL
    BEGIN
        ALTER DATABASE [$target] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    END;

    RESTORE DATABASE [$target] FROM DISK = N'$escapedFile' WITH $restoreOptions;
    ALTER DATABASE [$target] SET MULTI_USER;
END TRY
BEGIN CATCH
    BEGIN TRY
        IF DB_ID(N'$target') IS NOT NULL
        BEGIN
            ALTER DATABASE [$target] SET MULTI_USER;
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
Write-Host "Database restored successfully: $target"
