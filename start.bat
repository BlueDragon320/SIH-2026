@echo off
title Air-Gapped Agentic AI Workbench Launcher
echo ================================================================================
echo Starting Air-Gapped Agentic AI Workbench...
echo ================================================================================
echo.

echo Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Workbench FastAPI Backend" cmd /k "python -m uvicorn orchestrator.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Launching React Web UI on http://127.0.0.1:5173 ...
start "Workbench React UI" cmd /k "cd frontend-web && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo ================================================================================
echo Workbench servers started successfully!
echo Open your browser at: http://127.0.0.1:5173
echo ================================================================================
