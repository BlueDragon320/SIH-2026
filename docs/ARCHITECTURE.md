# Air-Gapped Agentic AI Workbench — Architecture Guide

## 1. System Overview
The Air-Gapped Agentic AI Workbench provides self-hosted, multi-model agentic AI workflows on enterprise/industrial premises without any external network dependency.

All components run strictly offline:
- **Serving Layer**: Stock Ollama with residency and concurrency configuration.
- **Control Plane**: FastAPI orchestrator with dynamic model registry, task routing, and autonomous agent state machine.
- **Tool Sandbox**: Linux kernel namespace isolation (`bwrap --unshare-net` with `prlimit` resource limits).
- **RAG / Vector Store**: Local ChromaDB collection with `nomic-embed-text` embeddings and BM25 hybrid ranking.
- **Multimodal Ingestion**: PyMuPDF + Moondream / Qwen2-VL vision OCR.
- **Deliverables**: Native Word (`.docx`), PowerPoint (`.pptx`), and Audited Excel (`.xlsx`) generation with live formulas and summary sheets.
- **Air-Gap Verification**: Real-time interface/socket monitor (`network_monitor/monitor.py`) proving zero external egress.

---

## 2. Directory Structure
```
SIH/
├── docker-compose.yml              # Isolated bridge network definition
├── docs/                           # Architecture docs & spec
│   ├── ARCHITECTURE.md
│   └── air-gapped-agentic-ai-workbench-spec.md
├── network_monitor/                # Real-time egress proof monitor
│   └── monitor.py
├── orchestrator/
│   ├── main.py                     # FastAPI REST API & endpoints
│   ├── agent/
│   │   ├── graph.py                # Plan -> Act -> Observe -> Reflect loop
│   │   └── memory.py               # SQLite task state persistence
│   ├── audit/
│   │   └── logger.py               # Dual SQLite + JSONL audit trail
│   ├── auth/                       # JWT authentication & session management
│   ├── ingestion/
│   │   ├── folder_watcher.py       # Knowledge base background directory watcher
│   │   ├── loaders.py              # PDF/DOCX/CSV/TXT loader
│   │   └── ocr_pipeline.py         # Multimodal VLM OCR extraction
│   ├── rag/
│   │   ├── embed.py                # Local Ollama embedding client
│   │   └── vector_store.py         # ChromaDB store with metadata & hybrid search
│   ├── router/
│   │   ├── classifier.py           # Multi-intent task classifier
│   │   ├── registry.yaml           # Model capabilities & VRAM config
│   │   └── selector.py             # Dynamic model selector & router
│   └── tools/
│       ├── docgen.py               # Word (.docx) & PPTX generator
│       ├── files.py                # Workspace path-confined file R/W
│       ├── rag_search.py           # Hybrid knowledge retrieval
│       ├── sandbox.py              # Bubblewrap network-isolated execution
│       ├── spreadsheet.py          # Audited multi-sheet Excel generator
│       └── vision_ocr.py           # Vision OCR tool re-export
├── frontend/                       # Streamlit UI
├── frontend-web/                   # React 19 + TypeScript + Vite UI
├── models/
│   └── Modelfiles/                 # Custom Modelfiles
└── data/
    ├── knowledge_base/             # Ingested SOPs, standards, and manuals
    ├── workspace/                  # Agent scratch space and deliverables
    └── chroma_db/                  # Persistent ChromaDB embeddings
```

---

## 3. Security & Isolation Boundary
1. **Network Namespace**: Code execution runs via Bubblewrap (`bwrap --unshare-net --unshare-ipc --unshare-pid`) preventing all network packet egress.
2. **Resource Constraints**: Virtual memory (`prlimit --as`) and CPU time (`prlimit --cpu`) quotas enforced on all untrusted sandbox executions.
3. **Workspace Allowlist**: File tool strictly validates canonical paths within `data/workspace` to prevent directory traversal attacks.
4. **Audit Logging**: Dual-write append-only JSONL and SQLite tables capture hashes, model selections, tool parameters, and execution outcomes.
