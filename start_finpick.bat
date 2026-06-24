@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "BACKEND_PY=%BACKEND%\.venv\Scripts\python.exe"
set "BACKEND_PY_ALT=%BACKEND%\venv\Scripts\python.exe"
set "PYTHON311=C:\Users\SSAFY\AppData\Local\Programs\Python\Python311\python.exe"

echo.
echo ========================================
echo FinPick - start all servers
echo ========================================
echo Backend : http://127.0.0.1:8000/api/
echo Frontend: http://127.0.0.1:5173/
echo.

if not exist "%BACKEND%" (
  echo ERROR: backend folder was not found.
  pause
  exit /b 1
)

if not exist "%FRONTEND%" (
  echo ERROR: frontend folder was not found.
  pause
  exit /b 1
)

call "%ROOT%stop_finpick.bat" nopause

if exist "%BACKEND_PY%" (
  start "FinPick Backend" cmd /k "cd /d "%BACKEND%" && "%BACKEND_PY%" manage.py runserver 127.0.0.1:8000 --noreload"
) else if exist "%BACKEND_PY_ALT%" (
  start "FinPick Backend" cmd /k "cd /d "%BACKEND%" && "%BACKEND_PY_ALT%" manage.py runserver 127.0.0.1:8000 --noreload"
) else if exist "%PYTHON311%" (
  start "FinPick Backend" cmd /k "cd /d "%BACKEND%" && "%PYTHON311%" manage.py runserver 127.0.0.1:8000 --noreload"
) else (
  start "FinPick Backend" cmd /k "cd /d "%BACKEND%" && py -3.11 manage.py runserver 127.0.0.1:8000 --noreload"
)

start "FinPick Frontend" cmd /k "cd /d "%FRONTEND%" && npm.cmd run dev -- --host 127.0.0.1 --port 5173"

echo.
echo Started.
echo Open http://127.0.0.1:5173/
echo.
pause