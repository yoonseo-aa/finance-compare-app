@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"
set "BACKEND_PY=%BACKEND%\.venv\Scripts\python.exe"
set "BACKEND_PIP=%BACKEND%\.venv\Scripts\pip.exe"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%NPM%" set "NPM=npm"

echo.
echo Starting FinPick development servers...
echo Backend API : http://127.0.0.1:8000/api/
echo Frontend    : http://127.0.0.1:5173/
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

if not exist "%BACKEND%\.env" (
  echo Creating backend .env from .env.example...
  copy "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
)

if not exist "%BACKEND_PY%" (
  echo Creating backend virtual environment...
  py -3 -m venv "%BACKEND%\.venv"
  if errorlevel 1 (
    python -m venv "%BACKEND%\.venv"
  )
)

if not exist "%BACKEND_PY%" (
  echo ERROR: Python virtual environment could not be created.
  pause
  exit /b 1
)

if not exist "%BACKEND%\db.sqlite3" (
  echo Initializing backend...
  "%BACKEND_PIP%" install -r "%BACKEND%\requirements.txt"
  if errorlevel 1 goto fail
  "%BACKEND_PY%" "%BACKEND%\manage.py" makemigrations
  if errorlevel 1 goto fail
  "%BACKEND_PY%" "%BACKEND%\manage.py" migrate
  if errorlevel 1 goto fail
  "%BACKEND_PY%" "%BACKEND%\manage.py" seed_demo
  if errorlevel 1 goto fail
)

if not exist "%FRONTEND%\node_modules" (
  echo Installing frontend packages...
  pushd "%FRONTEND%"
  call "%NPM%" install
  if errorlevel 1 (
    popd
    goto fail
  )
  popd
)

echo Opening backend server window...
start "FinPick Backend" "%ROOT%scripts\start_backend.bat"

echo Opening frontend server window...
start "FinPick Frontend" "%ROOT%scripts\start_frontend.bat"

echo.
echo Done.
echo Open http://127.0.0.1:5173/ in your browser.
echo To stop servers, close the opened windows or run stop_finpick.bat.
echo.
pause
exit /b 0

:fail
echo.
echo ERROR: Setup failed. Check the message above.
pause
exit /b 1
