@echo off
setlocal
title Geo-Agents

set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"
set PORT=8084

if "%1"=="" goto menu
if "%1"=="start" goto start
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="dashboard" goto dashboard
if "%1"=="api" goto api
if "%1"=="clean" goto clean
if "%1"=="chat" goto chat
goto help

:menu
echo.
echo  ============================================================
echo   Geo-Agents — LangGraph Multi-Agent Platform
echo  ============================================================
echo.
echo   Usage:  run.bat [command]
echo.
echo   Commands:
echo     start       Start server and open dashboard
echo     install     Install dependencies (first time setup)
echo     test        Run all tests
echo     dashboard   Open dashboard in browser
echo     api         Open API docs in browser
echo     chat        Quick test: send a chat message
echo     clean       Remove build artifacts and caches
echo     help        Show this message
echo.
echo   Example:
echo     run.bat install     -- first time setup
echo     run.bat start       -- start server + open dashboard
echo     run.bat test        -- verify everything works
echo.
goto end

:start
echo.
echo  ============================================================
echo   Starting Geo-Agents Server
echo  ============================================================
echo.
echo   Dashboard:  http://localhost:%PORT%/
echo   API Docs:   http://localhost:%PORT%/docs
echo   Health:     http://localhost:%PORT%/health
echo.

:: Open dashboard after delay
start "" /min cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:%PORT%/"

:: Start server with auto-reload
python -m uvicorn geo_agents.main:app --host 0.0.0.0 --port %PORT% --reload
goto end

:install
echo.
echo [1/3] Installing project in editable mode with dev dependencies...
pip install -e ".[dev]"
if errorlevel 1 (
    echo.
    echo ERROR: Install failed. Make sure Python 3.11+ and pip are on PATH.
    goto end
)
echo.
echo [2/3] Copying .env.example to .env (if not exists)...
if not exist ".env" (
    copy .env.example .env
    echo     Created .env from .env.example
) else (
    echo     .env already exists, skipping
)
echo.
echo [3/3] Verifying installation...
python -c "import geo_agents; print('  geo_agents', geo_agents.__version__)"
python -c "from geo_agents.graph import agent_graph; print('  LangGraph OK')"
python -c "from geo_agents.tools.registry import get_tool_names; print('  Tools OK:', len(get_tool_names()), 'tools')"
echo.
echo Setup complete. Run 'run.bat start' to launch the server.
goto end

:test
echo.
echo Running test suite...
echo.
pytest tests/ -v --tb=short
if errorlevel 1 (
    echo.
    echo Some tests failed. Check output above.
) else (
    echo.
    echo All tests passed.
)
goto end

:dashboard
:: Check if server is running
curl -s http://localhost:%PORT%/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Server not running on port %PORT%.
    echo  Run 'run.bat start' first.
    goto end
)
echo  Opening dashboard...
start http://localhost:%PORT%/
goto end

:api
:: Check if server is running
curl -s http://localhost:%PORT%/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Server not running on port %PORT%.
    echo  Run 'run.bat start' first.
    goto end
)
echo  Opening API docs...
start http://localhost:%PORT%/docs
goto end

:chat
:: Check if server is running
curl -s http://localhost:%PORT%/health >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Server not running on port %PORT%.
    echo  Run 'run.bat start' first.
    goto end
)
echo.
echo  Sending test message to agent...
echo.
curl -s -X POST http://localhost:%PORT%/api/chat -H "Content-Type: application/json" -d "{\"message\":\"What are the current weather conditions for drone flight planning at lat 40.71, lon -74.01?\"}"
echo.
echo.
goto end

:clean
echo.
echo Cleaning build artifacts...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build
for /d /r . %%d in (__pycache__) do if exist "%%d" rmdir /s /q "%%d"
for /d /r . %%d in (.pytest_cache) do if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
echo Done.
goto end

:help
echo.
echo Unknown command: %1
echo Run 'run.bat' with no arguments to see available commands.
goto end

:end
endlocal
