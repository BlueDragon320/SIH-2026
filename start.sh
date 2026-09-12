#!/usr/bin/env bash
# ==============================================================================
# Air-Gapped Agentic AI Workbench - Quick Launch Executable
# Starts: Ollama, FastAPI Orchestrator, Modern React Web UI
# Automatically redirects and opens browser to http://localhost:5173
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/start_workbench.sh" "$@"
