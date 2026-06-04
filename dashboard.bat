@echo off
setlocal

:: ============================================================
::  Geo-Agents — Open Dashboard
:: ============================================================

set PORT=8084

:: Check if server is running
curl -s http://localhost:%PORT%/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Server not running on port %PORT%.
    echo  Starting server first...
    echo.
    start "Geo-Agents Server" cmd /c "cd /d "%~dp0" && start.bat"
    timeout /t 4 /nobreak >nul
)

echo  Opening dashboard...
start http://localhost:%PORT%/

endlocal
