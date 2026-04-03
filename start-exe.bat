@echo off
title MyInfoManager

echo ========================================
echo    MyInfoManager - Starting
echo ========================================
echo.

cd /d "%~dp0"

:: Check if EXE exists
if not exist "dist\MyInfoManager\MyInfoManager.exe" (
    echo [ERROR] MyInfoManager.exe not found!
    echo Run: pyinstaller MyInfoManager.spec
    pause
    exit /b 1
)

echo [*] Starting...
echo [*] Browser will open automatically
echo [*] Press Ctrl+C in this window to stop
echo.

dist\MyInfoManager\MyInfoManager.exe

pause
