@echo off
title MyInfoManager - Stop

echo ========================================
echo    MyInfoManager - Stopping
echo ========================================
echo.

taskkill /FI "WINDOWTITLE eq MyInfoManager Server*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo [*] Server stopped
) else (
    echo [!] Server was not running
)

echo.
pause
