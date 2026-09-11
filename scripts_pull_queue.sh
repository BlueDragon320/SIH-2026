#!/bin/bash
echo "[1/2] Pulling llama3.1:8b..."
ollama pull llama3.1:8b
echo "[2/2] Pulling qwen2.5-math:7b..."
ollama pull qwen2.5-math:7b
echo "All target models downloaded successfully!"
