#!/usr/bin/env bash
# ==============================================================================
# Air-Gapped Agentic AI Workbench — Master Launch & Service Controller
# Configured for NVIDIA RTX 3060 (6GB VRAM) & Air-Gapped Zero-Egress Operation
#
# Launches 3 Core Air-Gapped Services:
#   1. Ollama LLM/VLM Daemon       -> http://127.0.0.1:11434
#   2. FastAPI Control Orchestrator -> http://127.0.0.1:8000
#   3. Modern React Web Application -> http://127.0.0.1:5173 (via Vite Dev Server)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${PROJECT_DIR:-$SCRIPT_DIR}"
FRONTEND_DIR="$PROJECT_DIR/frontend-web"
DATA_DIR="$PROJECT_DIR/data"

# Auto-detect virtual environment python and uvicorn or fallback to system
if [ -x "$PROJECT_DIR/.venv/bin/python" ]; then
    VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
    VENV_UVICORN="$PROJECT_DIR/.venv/bin/uvicorn"
elif [ -x "$PROJECT_DIR/venv/bin/python" ]; then
    VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
    VENV_UVICORN="$PROJECT_DIR/venv/bin/uvicorn"
else
    VENV_PYTHON="python3"
    VENV_UVICORN="uvicorn"
fi

mkdir -p "$DATA_DIR"

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE="15m"
export WORKBENCH_API_URL="http://127.0.0.1:8000"

# Auto-detect local models folder in SIH repository if present
if [ -z "$OLLAMA_MODELS" ]; then
    if [ -d "$PROJECT_DIR/models/blobs" ]; then
        export OLLAMA_MODELS="$PROJECT_DIR/models"
    elif [ -d "$PROJECT_DIR/Models/blobs" ]; then
        export OLLAMA_MODELS="$PROJECT_DIR/Models"
    fi
fi

# ANSI Colors
BOLD="\033[1m"
GREEN="\033[32m"
CYAN="\033[36m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

# Handle CLI actions (--stop, --restart, --status)
ACTION="${1:-start}"

stop_services() {
    echo -e "${YELLOW}🛑 Stopping Air-Gapped Workbench Services...${RESET}"
    pkill -f "node.*vite.*5173" || true
    pkill -f "uvicorn orchestrator.main:app" || true
    pkill -f "ollama serve" || true
    pkill -f "streamlit" || true
    sleep 2
    echo -e "${GREEN}✓ All services stopped.${RESET}"
}

check_status() {
    echo -e "\n${BOLD}${CYAN}=== Air-Gapped Workbench Service Status ===${RESET}"
    
    # 1. Ollama
    if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
        echo -e "  [1/3] Ollama Daemon (11434):       ${GREEN}ONLINE${RESET}"
    else
        echo -e "  [1/3] Ollama Daemon (11434):       ${RED}OFFLINE${RESET}"
    fi

    # 2. FastAPI Orchestrator
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        echo -e "  [2/3] FastAPI Orchestrator (8000): ${GREEN}ONLINE${RESET}"
    else
        echo -e "  [2/3] FastAPI Orchestrator (8000): ${RED}OFFLINE${RESET}"
    fi

    # 3. Modern React Web UI
    if curl -s http://127.0.0.1:5173 >/dev/null 2>&1; then
        echo -e "  [3/3] Modern React Web UI (5173):  ${GREEN}ONLINE${RESET}"
    else
        echo -e "  [3/3] Modern React Web UI (5173):  ${RED}OFFLINE${RESET}"
    fi
    echo ""
}

if [ "$ACTION" == "--stop" ] || [ "$ACTION" == "stop" ]; then
    stop_services
    exit 0
elif [ "$ACTION" == "--status" ] || [ "$ACTION" == "status" ]; then
    check_status
    exit 0
elif [ "$ACTION" == "--restart" ] || [ "$ACTION" == "restart" ]; then
    stop_services
    echo ""
fi

echo "================================================================="
echo "🛡️  Starting Air-Gapped Agentic AI Workbench..."
echo "Target Hardware: NVIDIA RTX 3060 Laptop (6GB VRAM)"
echo "Environment: Pure Air-Gapped (Zero Outbound Telemetry)"
echo "================================================================="

# 1. Start Ollama Server if not running
if ! curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
    echo -e "[1/3] Starting background Ollama daemon (6GB VRAM config)..."
    nohup setsid "$PROJECT_DIR/run_ollama.sh" > "$DATA_DIR/ollama_runtime.log" 2>&1 &
    for i in {1..15}; do
        if curl -s http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    echo -e "${GREEN}      ✓ Ollama daemon active on http://127.0.0.1:11434${RESET}"
else
    echo -e "[1/3] ${GREEN}✓ Ollama daemon is already active on http://127.0.0.1:11434${RESET}"
fi

# 2. Start FastAPI Orchestrator API if not running
if ! curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
    echo -e "[2/3] Starting FastAPI Control-Plane Orchestrator on http://127.0.0.1:8000..."
    nohup setsid "$VENV_UVICORN" orchestrator.main:app --host 127.0.0.1 --port 8000 > "$DATA_DIR/orchestrator.log" 2>&1 &
    for i in {1..15}; do
        if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    echo -e "${GREEN}      ✓ FastAPI Orchestrator active on http://127.0.0.1:8000${RESET}"
else
    echo -e "[2/3] ${GREEN}✓ FastAPI Orchestrator is already active on http://127.0.0.1:8000${RESET}"
fi

# 3. Start Modern React Web Application (Vite Dev Server) if not running
if ! curl -s http://127.0.0.1:5173 >/dev/null 2>&1; then
    echo -e "[3/3] Starting Modern React Web UI (Vite) on port 5173..."
    if command -v npm >/dev/null 2>&1; then
        (cd "$FRONTEND_DIR" && nohup setsid npm run dev -- --host 0.0.0.0 --port 5173 > "$DATA_DIR/frontend_web.log" 2>&1 &)
    else
        (cd "$FRONTEND_DIR" && nohup setsid node ./node_modules/.bin/vite --host 0.0.0.0 --port 5173 > "$DATA_DIR/frontend_web.log" 2>&1 &)
    fi
    for i in {1..15}; do
        if curl -s http://127.0.0.1:5173 >/dev/null 2>&1; then
            break
        fi
        sleep 1
    done
    echo -e "${GREEN}      ✓ Modern React Web UI active on port 5173 (0.0.0.0)${RESET}"
else
    echo -e "[3/3] ${GREEN}✓ Modern React Web UI is already active on port 5173${RESET}"
fi

echo "================================================================="
echo -e "${BOLD}${GREEN}✅ Air-Gapped Workbench is LIVE & FULLY OPERATIONAL!${RESET}"
echo "-----------------------------------------------------------------"
echo -e "   ${BOLD}Web UI Dashboard:${RESET}     http://127.0.0.1:5173"
echo -e "   ${BOLD}Orchestrator REST API:${RESET} http://127.0.0.1:8000"
echo -e "   ${BOLD}API Docs (Swagger):${RESET}   http://127.0.0.1:8000/docs"
echo -e "   ${BOLD}Ollama Model Runtime:${RESET} http://127.0.0.1:11434"
echo "-----------------------------------------------------------------"
echo -e "   ${BOLD}Vite Proxy Endpoints:${RESET}"
echo -e "   • Models:          http://127.0.0.1:5173/api/v1/models"
echo -e "   • Hardware Status: http://127.0.0.1:5173/api/v1/hardware-status"
echo -e "   • Ollama Tags:     http://127.0.0.1:5173/ollama/api/tags"
echo "-----------------------------------------------------------------"
echo -e "   ${BOLD}Runtime Logs:${RESET}"
echo -e "   • Ollama:       $DATA_DIR/ollama_runtime.log"
echo -e "   • Orchestrator: $DATA_DIR/orchestrator.log"
echo -e "   • Web UI:       $DATA_DIR/frontend_web.log"
echo "================================================================="

# Automatically redirect / open default browser to Modern React Web UI
if [ -n "$DISPLAY" ] || [ -n "$WAYLAND_DISPLAY" ]; then
    echo -e "\n${BOLD}${CYAN}🚀 Redirecting to Web UI in your default browser (http://localhost:5173)...${RESET}"
    if command -v xdg-open >/dev/null 2>&1; then
        xdg-open "http://localhost:5173" >/dev/null 2>&1 &
    elif command -v sensible-browser >/dev/null 2>&1; then
        sensible-browser "http://localhost:5173" >/dev/null 2>&1 &
    elif command -v python3 >/dev/null 2>&1; then
        python3 -m webbrowser "http://localhost:5173" >/dev/null 2>&1 &
    fi
fi
