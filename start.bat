@echo off
title MyInfoManager

echo ========================================
echo    MyInfoManager - Starting
echo ========================================
echo.

:: Check if server is already running
tasklist /FI "WINDOWTITLE eq MyInfoManager Server*" 2>nul | find /I "python" >nul
if %errorlevel%==0 (
    echo [!] Server already running. Close previous instance or use stop.bat
    pause
    exit /b 1
)

:: Go to script directory
cd /d "%~dp0"

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.11+
    pause
    exit /b 1
)

:: Create virtual environment if not exists
if not exist "venv\" (
    echo [*] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies
echo [*] Checking dependencies...
pip install -q -r requirements.txt

:: Build frontend if not built
if not exist "sidebar\build\index.html" (
    echo [*] Building frontend...
    cd sidebar
    call npm install --silent
    call npm run build
    if %errorlevel% neq 0 (
        echo [ERROR] Frontend build failed
        cd ..
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo [*] Starting server...
echo [*] Browser will open automatically
echo [*] Press Ctrl+C in this window to stop
echo.

:: Start server in separate window
start "MyInfoManager Server" cmd /c "call %~dp0venv\Scripts\activate.bat && uvicorn server.main:app --host 127.0.0.1 --port 8000 --log-level info"

:: Wait for server to start
echo [*] Waiting for server...
timeout /t 3 /nobreak >nul

:: Open browser
start http://localhost:8000

echo.
echo ========================================
echo    MyInfoManager is running!
echo    Close this window to stop
echo ========================================

:: Wait for user to close
pause >nul

:: Stop server on close
echo [*] Stopping server...
taskkill /FI "WINDOWTITLE eq MyInfoManager Server*" /T /F >nul 2>&1
echo [*] Server stopped
