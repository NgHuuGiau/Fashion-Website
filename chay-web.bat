@echo off
cd /d "%~dp0"
rem Dung: chay-web.bat           -> chi may minh
rem        chay-web.bat lan       -> ca may khac trong LAN (mo http://IP-LAN:8000)
if /i "%~1"=="lan" (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\start.ps1" -Lan
) else (
    powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\start.ps1"
)
pause
pause