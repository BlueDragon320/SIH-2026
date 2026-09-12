#!/usr/bin/env bash
# run_ollama.sh - Launches Ollama configured for RTX 3060 (6GB VRAM)
set -e

# Auto-detect local models folder if present in project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -z "$OLLAMA_MODELS" ]; then
    if [ -d "$SCRIPT_DIR/models/blobs" ]; then
        export OLLAMA_MODELS="$SCRIPT_DIR/models"
    elif [ -d "$SCRIPT_DIR/Models/blobs" ]; then
        export OLLAMA_MODELS="$SCRIPT_DIR/Models"
    fi
fi

export OLLAMA_HOST="127.0.0.1:11434"
export OLLAMA_MAX_LOADED_MODELS=2
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE="15m"
export OLLAMA_FLASH_ATTENTION=1

echo "Starting Ollama daemon on $OLLAMA_HOST (Max Loaded Models: $OLLAMA_MAX_LOADED_MODELS, Parallel: $OLLAMA_NUM_PARALLEL, Models Path: ${OLLAMA_MODELS:-default})..."
exec /usr/local/bin/ollama serve
