@echo off
setlocal
title Geo-Agents Server

:: ============================================================
::  Geo-Agents — Start Server & Open Dashboard
:: ============================================================

set PORT=8084

echo.
echo  ============================================================
echo   Geo-Agents — Starting Server
echo  ============================================================
echo.
echo   Dashboard:  http://localhost:%PORT%/
echo   API Docs:   http://localhost:%PORT%/docs
echo   Health:     http://localhost:%PORT%/health
echo.
echo   Press Ctrl+C to stop the server.
echo.

:: Open dashboard in default browser after 3 second delay
start "" /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:%PORT%/"

:: Start the server
python -m uvicorn geo_agents.main:app --host 0.0.0.0 --port %PORT% --reload

endlocal
