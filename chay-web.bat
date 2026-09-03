@echo off
cd /d "%~dp0backend"
echo Dang khoi dong web tai https://127.0.0.1:8000/ ...
echo (Nhan Ctrl+C de tat. Neu dong cua so ma webserver treo, lan chay sau tu dong don)
"C:\Users\HUUGIAU\OneDrive\Documents\GitHub\Fashion-Website\.venv\Scripts\python.exe" run_local.py 127.0.0.1 8000
pause
