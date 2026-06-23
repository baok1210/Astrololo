@echo off
title Astrololo WebUI
cd /d "%~dp0"

echo [Astrololo] Starting backend...
start "Astrololo Backend" /min cmd /c "cd /d %CD%\backend && uvicorn astrololo.api.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 /nobreak >nul

echo [Astrololo] Starting frontend...
start "Astrololo Frontend" /min cmd /c "cd /d %CD%\frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ==========================================
echo   Astrololo is running!
echo.
echo   Frontend: http://localhost:5173
echo   Backend : http://localhost:8000
echo ==========================================
echo.
start http://localhost:5173
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /f /fi "WINDOWTITLE eq Astrololo Backend" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Astrololo Frontend" >nul 2>&1
echo Done.
