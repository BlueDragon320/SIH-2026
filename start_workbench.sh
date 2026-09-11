#!/usr/bin/env bash
# ==============================================================================
# Air-Gapped Agentic AI Workbench — Master Launch & Service Controller
# Configured for NVIDIA RTX 3060 (6GB VRAM) & Air-Gapped Zero-Egress Operation
# ==============================================================================

set -e

PROJECT_DIR="/home/blue/SIH"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
VENV_STREAMLIT="$PROJECT_DIR/.venv/bin/streamlit"
VENV_UVICORN="$PROJECT_DIR/.venv/bin/uvicorn"

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE="15m"
export WORKBENCH_API_URL="http://127.0.0.1:8000"

echo "================================================================="
echo "🛡️ Starting Air-Gapped Agentic AI Workbench..."
echo "Target Hardware: NVIDIA RTX 3060 Laptop (6GB VRAM)"
echo "Environment: Pure Air-Gapped (Zero Outbound Telemetry)"
echo "================================================================="

# 1. Start Ollama Server if not running
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo "[1/3] Starting background Ollama daemon (6GB VRAM config)..."
    /home/blue/SIH/run_ollama.sh > "$PROJECT_DIR/data/ollama_runtime.log" 2>&1 &
    sleep 3
else
    echo "[1/3] Ollama daemon is already active on 127.0.0.1:11434."
fi

# 2. Start FastAPI Orchestrator API
echo "[2/3] Starting FastAPI Control-Plane Orchestrator on http://127.0.0.1:8000..."
nohup $VENV_UVICORN orchestrator.main:app --host 127.0.0.1 --port 8000 > "$PROJECT_DIR/data/orchestrator.log" 2>&1 &
sleep 2

# 3. Start Streamlit Interactive Frontend
echo "[3/3] Starting Streamlit Interactive Workbench on http://127.0.0.1:8501..."
nohup $VENV_STREAMLIT run frontend/app.py --server.port 8501 --server.headless true > "$PROJECT_DIR/data/frontend.log" 2>&1 &
sleep 2

echo "================================================================="
echo "✅ Air-Gapped Workbench is LIVE!"
echo "   - Web UI Dashboard:     http://127.0.0.1:8501"
echo "   - Orchestrator REST API: http://127.0.0.1:8000"
echo "   - API Docs (Swagger):   http://127.0.0.1:8000/docs"
echo "   - Ollama Model Runtime: http://127.0.0.1:11434"
echo "================================================================="
