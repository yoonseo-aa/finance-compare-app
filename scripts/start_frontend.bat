@echo off
setlocal

set "ROOT=%~dp0.."
set "FRONTEND=%ROOT%\frontend"
set "NPM=C:\Program Files\nodejs\npm.cmd"

if not exist "%NPM%" set "NPM=npm"

cd /d "%FRONTEND%"

echo FinPick Frontend
echo URL: http://127.0.0.1:5173/
echo.

call "%NPM%" run dev
pause
