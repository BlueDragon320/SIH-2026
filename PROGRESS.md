# Air-Gapped Agentic AI Workbench — Project Progress & Phase Tracker

## System Constraints & Resource Profile
- **Target Hardware**: NVIDIA GeForce RTX 3060 Laptop (6GB VRAM)
- **Host Memory**: 27 GB RAM
- **Disk Allocation Limit**: < 30 GB total (Available: ~28 GB)
- **Model Lineup (< 8 GB total storage, < 5.5 GB VRAM peak)**:
  - **Reasoning & Coding**: `qwen2.5-coder:3b` (~1.9 GB) / `qwen2.5-coder:7b` (~4.7 GB)
  - **Vision & OCR**: `moondream` (1.8B, ~1.7 GB) / `qwen2-vl:2b` (~2.2 GB)
  - **Local Embeddings**: `nomic-embed-text` (~274 MB)
- **Isolation Mechanism**: Rootless `bwrap` (Bubblewrap) network unshare (`--unshare-net`) + Docker isolated bridge fallback + local packet egress auditor.

---

## Phase Breakdown & Status

### Phase 0: Infra & Runtime Setup
- [x] Initialize Python virtual environment & core dependencies (FastAPI, Uvicorn, LangGraph/StateGraph, Pydantic, python-docx, python-pptx, openpyxl, ChromaDB, PyMuPDF, Pillow, psutil, Streamlit)
- [x] Configure & launch Ollama service with 6GB VRAM optimizations (`OLLAMA_MAX_LOADED_MODELS=2`, `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_KEEP_ALIVE=15m`)
- [x] Pull and verify lightweight 3-model suite (`qwen2.5-coder:3b`, `moondream`, `nomic-embed-text`)
- [x] Verify GPU acceleration and memory footprint via `nvidia-smi` and Ollama `/api/ps`

### Phase 1: Model Registry & Task Router
- [x] Create `orchestrator/router/registry.yaml` schema with capability mappings and VRAM budgets
- [x] Implement `orchestrator/router/classifier.py` for instant task classification (`code_gen`, `code_review`, `doc_summarize`, `doc_draft`, `vision_ocr`, `spreadsheet_calc`, `general_qa`, `multi_step_plan`)
- [x] Implement VRAM-aware model selector with fallback handling
- [x] Implement dynamic model registration endpoint (`POST /v1/models/register`) allowing hot addition of models without server restart
- [x] Log and query all routing decisions with clear audit traces

### Phase 2: Agent Orchestration Core
- [x] Implement Plan → Act → Observe → Reflect → Self-Correct state machine loop (`orchestrator/agent/graph.py`)
- [x] Implement SQLite task persistence & resumability (`orchestrator/agent/memory.py` / `db.py`)
- [x] Implement structured function-calling parser compatible with local Ollama models
- [x] Implement Human-in-the-Loop approval checkpoints (`POST /v1/task/{id}/approve`)

### Phase 3: Secure Tool Layer
- [x] **File R/W Tool**: Path-allowlisted sandbox workspace file operations (`orchestrator/tools/files.py`)
- [x] **Code Sandbox Tool**: Secure ephemeral code execution with network isolation (`--network none` via `bwrap`/container) (`orchestrator/tools/sandbox.py`)
- [x] **Spreadsheet Tool**: Audit-ready Excel calculation engine with live formula generation via `openpyxl` (`orchestrator/tools/spreadsheet.py`)
- [x] **Document Generation Tool**: Real `.docx` (approval notes/reports) & `.pptx` (executive decks) generator (`orchestrator/tools/docgen.py`)

### Phase 4: Multimodal Ingestion Pipeline
- [x] MIME & file type detection (native text PDF/DOCX vs scanned image/drawings)
- [x] Vision-language OCR & layout extractor via local vision model (`orchestrator/ingestion/ocr_pipeline.py`)
- [x] Structured extraction schema (`raw_text`, `tables`, `key_value_fields`, `confidence`)

### Phase 5: Local Knowledge Base & Air-Gapped RAG
- [x] Embedded local Vector Store (`ChromaDB`) with zero external network dependencies
- [x] Document chunker & Ollama local embedding client (`orchestrator/rag/embed.py`)
- [x] Hybrid BM25 keyword + Vector retrieval with exact document & section citation tracking
- [x] Folder watcher for automated background ingestion of SOPs, manuals, and technical docs

### Phase 6: Air-Gap Enforcement, Egress Monitor & Audit Proof
- [x] Zero-egress network isolation verification
- [x] Real-time local network monitor service measuring external interface traffic (`network_monitor/monitor.py`)
- [x] Comprehensive immutable local audit logger (`orchestrator/audit/logger.py`) recording all tool invocations, model calls, prompt hashes, and token metrics

### Phase 7: Interactive Web UI & Live Demo Workbench
- [x] Modern React Web Application (`frontend-web` on port 5173):
  - High-performance Vite frontend with Tailwind CSS and responsive multi-panel layout
  - Direct reverse proxies for `/api` (FastAPI 8000) and `/ollama` (Ollama 11434)
  - Real-time hardware telemetry, model routing status, agent timeline, and workspace management
- [x] Master startup script modernization (`start_workbench.sh`):
  - Clean lifecycle management for Ollama (11434), FastAPI (8000), and Vite (5173)
  - Automated healthchecks and status reporting (`--status`, `--stop`, `--restart`)
- [x] Streamlit/FastAPI interactive dashboard (`frontend/app.py`):
  - **Live Chat & Task Console**: Interactive chat with multi-file attachment upload
  - **Live Agent Timeline**: Real-time inspectable step trace (Plan, Act, Tool Call, Output, Reflection)
  - **Deliverable Browser**: Direct preview and download of generated `.docx`, `.xlsx`, `.pptx`, and `.py` files
  - **Air-Gap Network Monitor Panel**: Real-time graph showing 0 B/s outbound traffic proof
  - **Model Registry & VRAM Manager**: Live loaded model inspector and dynamic model registration form
  - **Knowledge Base Manager**: Drag-and-drop document ingestion and semantic search explorer
- [x] Automated test suite passing 46/46 unit & integration tests (`verify_all.py`) and all 6 DoD criteria
- [x] Live rehearsal with all active models loaded in Ollama runtime

---

## Deliverable Demo Milestones
1. [x] **Multi-Model Auto-Selection**: Visible routing of coding vs reasoning vs vision tasks.
2. [x] **End-to-End Agentic Task**: Scanned inspection report → OCR → key findings extraction → approval note `.docx` generation.
3. [x] **Coding Sandbox Task**: Code generation → network-isolated execution → automated test verification → runnable deliverable saved.
4. [x] **Multimodal Drawing/Note Task**: Visual analysis of engineering drawing/scanned note with structured field extraction.
5. [x] **Air-Gap Proof**: Continuous live 0-byte egress monitoring during all agent workflows.
6. [x] **Zero-Code New Model Registration**: Dynamic registration of a model via YAML/API without system restart.
