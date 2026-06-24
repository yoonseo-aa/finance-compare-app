@echo off
setlocal

echo Stopping FinPick development servers...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
  taskkill /PID %%a /F >nul 2>nul
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
  taskkill /PID %%a /F >nul 2>nul
)

echo Done.
pause
