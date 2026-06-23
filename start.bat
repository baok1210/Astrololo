@echo off
title Astrololo - Starting services...
echo ============================================
echo    Astrololo - WebUI Launcher
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.11+
    pause
    exit /b 1
)

:: Check if Node.js is available
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

:: Set project root
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo [1/4] Installing backend dependencies...
cd /d "%PROJECT_DIR%backend"
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] pip install failed, trying to install from pyproject.toml...
    pip install -e . >nul 2>&1
)
echo       Done.

echo [2/4] Installing frontend dependencies...
cd /d "%PROJECT_DIR%frontend"
call npm install >nul 2>&1
echo       Done.

echo [3/4] Starting backend at http://localhost:8000 ...
cd /d "%PROJECT_DIR%backend"
start "Astrololo-Backend" cmd /c "uvicorn astrololo.api.main:app --host 0.0.0.0 --port 8000 --reload"
echo       Backend starting...

echo [4/4] Starting frontend at http://localhost:5173 ...
cd /d "%PROJECT_DIR%frontend"
start "Astrololo-Frontend" cmd /c "npm run dev"
echo       Frontend starting...

echo.
echo ============================================
echo    Services starting in separate windows:
echo.
echo    Backend : http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo    Press any key to open the Web UI in browser...
echo ============================================
pause >nul

:: Open the frontend in default browser
start http://localhost:5173

echo.
echo Web UI opened in browser. Close this window to stop?
echo (Close the service windows to stop servers)
pause
