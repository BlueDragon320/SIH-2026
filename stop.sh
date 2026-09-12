#!/usr/bin/env bash
# ==============================================================================
# Air-Gapped Agentic AI Workbench - Quick Stop Executable
# Gracefully stops: Vite Dev Server, FastAPI Orchestrator, Ollama Daemon
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/start_workbench.sh" --stop
