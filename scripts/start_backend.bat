@echo off
setlocal

set "ROOT=%~dp0.."
set "BACKEND=%ROOT%\backend"

cd /d "%BACKEND%"

echo FinPick Backend
echo URL: http://127.0.0.1:8000/api/
echo.

".venv\Scripts\python.exe" manage.py runserver 127.0.0.1:8000 --noreload
pause
