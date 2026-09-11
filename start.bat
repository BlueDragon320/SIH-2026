@echo off
title Air-Gapped Agentic AI Workbench Launcher
echo ================================================================================
echo Starting Air-Gapped Agentic AI Workbench...
echo ================================================================================
echo.

echo Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "Workbench FastAPI Backend" cmd /k "python -m uvicorn orchestrator.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo Launching Streamlit Frontend on http://127.0.0.1:8501 ...
start "Workbench Streamlit Frontend" cmd /k "streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1"

echo.
echo ================================================================================
echo Workbench servers started successfully!
echo Open your browser at: http://127.0.0.1:8501
echo ================================================================================
