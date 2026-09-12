@echo off
title Air-Gapped Agentic AI Workbench Launcher
cd /d "%~dp0"

echo ================================================================================
echo Starting Air-Gapped Agentic AI Workbench...
echo ================================================================================
echo.

REM Auto-detect local models folder if present
if exist "%~dp0models\blobs" set OLLAMA_MODELS=%~dp0models
if exist "%~dp0Models\blobs" set OLLAMA_MODELS=%~dp0Models

if not exist "%~dp0data" mkdir "%~dp0data"

REM 1. Check and start Ollama Daemon
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [1/3] Ollama daemon is already running (Port 11434)
) else (
    echo [1/3] Starting background Ollama daemon...
    start /B "Ollama Daemon" ollama serve > "%~dp0data\ollama_runtime.log" 2>&1
    timeout /t 2 /nobreak >nul
)

REM 2. Launch FastAPI Backend Orchestrator (Port 8000)
echo [2/3] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Workbench FastAPI Backend" cmd /k "python -m uvicorn orchestrator.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

REM 3. Launch Modern React Web UI (Port 5173)
echo [3/3] Launching Modern React Web UI on http://localhost:5173 ...
start "Workbench Web UI" cmd /k "cd frontend-web && npm run dev -- --host 0.0.0.0 --port 5173"

timeout /t 4 /nobreak >nul

echo.
echo ================================================================================
echo Air-Gapped Workbench started successfully!
echo Redirecting to: http://localhost:5173 ...
echo ================================================================================
start http://localhost:5173
