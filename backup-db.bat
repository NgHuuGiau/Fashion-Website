@echo off
setlocal
rem ============================================================
rem  Backup database HUUGIAU_Fashion moi ngay (giam lavan 7 ngay)
rem  Script nay chay thang bang sqlcmd (da cai san tren may).
rem
rem  Cach thu chay:      backup-db.bat
rem  Hen gio chay tu dong: Windows Task Scheduler -> moi ngay
rem  Muon don backup len cloud (Google Drive/OneDrive): chen lenh
rem  robocopy/ rclone ben duoi.
rem ============================================================

set "DB=HUUGIAU_Fashion"
set "BACKUP_DIR=%~dp0backups"

rem SQL Server chi ghi duoc vao noi co quyen. Da chay 1 lan:
rem   icacls "%~dp0backups" /grant "NT SERVICE\MSSQLSERVER:(OI)(CI)M"
rem neu loi Access denied khi backup.

if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set "TODAY=%%c%%a%%b"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "NOW=%%a%%b"

set "STAMP=%TODAY%_%NOW%"
set "FILE=%BACKUP_DIR%\%DB%_%STAMP%.bak"

echo [%date% %time%] Bat dau backup %DB% ...
sqlcmd -S . -C -E -d master -Q "BACKUP DATABASE [%DB%] TO DISK = N'%FILE%' WITH INIT, COMPRESSION" -b
if errorlevel 1 (
    echo [%date% %time%] LOI backup - kiem tra quyen ghi: icacls "%BACKUP_DIR%" /grant "NT SERVICE\MSSQLSERVER:(OI)(CI)M"
    exit /b 1
)
echo [%date% %time%] Da luu: %FILE%

rem Xoa backup cu hon 7 ngay
forfiles /p "%BACKUP_DIR%" /m *.bak /d -7 /c "cmd /c del @path" 2>nul

rem ============================================================
rem Tu dong day len cloud (mo ban, chu PRODUCT):
rem  robocopy "%BACKUP_DIR%" "C:\Users\HUUGIAU\OneDrive\Backups\Fashion" *.bak /MIR
rem  (hoac dung rclone:  rclone sync "%BACKUP_DIR%" remote:Backups/Fashion)
rem ============================================================

echo [%date% %time%] Xong backup.
exit /b 0