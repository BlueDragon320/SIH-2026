# Self-Hosted Agentic AI Workbench for Air-Gapped Industrial & Defence Environments

[![Air-Gap Certified](https://img.shields.io/badge/Air--Gap-100%25%20Verified%20Zero%20Egress-success)](#)
[![Hardware](https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203060%20(6GB%20VRAM)-blue)](#)
[![Model Serving](https://img.shields.io/badge/Runtime-Stock%20Ollama-orange)](#)

A fully self-hosted, air-gapped agentic AI workbench built for industrial, PSU, and defence environments where sensitive engineering documents, drawings, sensor telemetry, and approval notes **cannot** leave organization premises.

---

## 🚀 Key Features

1. **Multi-Model Auto-Routing & Dynamic Selection**:
   - Classifies tasks into coding, document drafting, spreadsheet calculations, RAG lookups, and visual inspection.
   - Automatically routes to the optimal local model (`qwen2.5-coder:3b`, `moondream`, `nomic-embed-text`) tailored for 6GB VRAM.
   - Hot dynamic registration of new models without system restarts or code redeployments.

2. **Autonomous Agent Loop (Plan → Act → Observe → Reflect → Self-Correct)**:
   - Deconstructs goals into ordered sub-steps.
   - Executes sandboxed tools, verifies outputs, and retries upon errors.
   - Full SQLite task persistence and inspectable live execution timeline.

3. **Secure Sandboxed Tool Layer**:
   - **Code Execution Sandbox**: Ephemeral execution using Linux kernel namespace isolation (`bwrap --unshare-net`) with 0 external network access.
   - **Spreadsheet Calculation Tool**: Produces `.xlsx` workbooks with live Excel formulas (`=SUM()`, `=AVERAGE()`) for auditable calculations.
   - **Document Generation Tool**: Generates authentic enterprise Word Approval Notes (`.docx`) and Executive PowerPoint Decks (`.pptx`).
   - **File Management**: Scoped to allowlisted sandbox workspace.

4. **Multimodal Ingestion & Local RAG**:
   - On-device Vision OCR (`moondream`) for scanned inspection reports and engineering diagrams.
   - Air-gapped ChromaDB vector store with hybrid (BM25 keyword + cosine semantic) search and source citation tracking.

5. **Live Air-Gap Proof & Network Egress Monitor**:
   - Real-time hardware socket and network interface egress meter proving **0.00 B/s outbound traffic**.
   - Immutable audit log recording every prompt hash, model invocation, and tool duration.

---

## 📦 Quick Start Guide

### 1. Start the Workbench
Run the master startup script:
```bash
./start_workbench.sh
```

This starts:
- **Ollama Serving Layer**: `http://127.0.0.1:11434` (Tuned for 6GB VRAM: `OLLAMA_MAX_LOADED_MODELS=2`)
- **FastAPI Control-Plane Orchestrator**: `http://127.0.0.1:8000`
- **Modern React Web UI (Vite)**: `http://127.0.0.1:5173` (with direct proxying to `/api` and `/ollama`)

### 2. Access the Web Dashboard
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in your browser.

---

## 🧪 Running Automated Verification
To verify all 6 Definition-of-Done criteria from the specification:
```bash
.venv/bin/python verify_all.py
```

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────┐
│     Modern React Web UI - Vite Frontend (Port 5173)    │
│  (Chat | Live Timeline | Deliverables | Egress Meter)  │
│      ├── Reverse Proxy `/api`    → http://127.0.0.1:8000
│      └── Reverse Proxy `/ollama` → http://127.0.0.1:11434
└───────────────────────────┬────────────────────────────┘
                            │ REST / Proxy
┌───────────────────────────▼────────────────────────────┐
│      FastAPI Orchestrator Control-Plane (Port 8000)    │
│  ┌────────────────────────┐  ┌──────────────────────┐  │
│  │ Task Router & Registry │  │ Agent State Graph    │  │
│  └────────────────────────┘  └──────────────────────┘  │
└───────────────────────────┬────────────────────────────┘
                            │ Secure Tool Invocations
   ┌────────────┬───────────┼───────────┬────────────┐
   ▼            ▼           ▼           ▼            ▼
┌─────────┐┌──────────┐┌─────────┐┌──────────┐┌───────────┐
│File R/W ││bwrap Code││Excel    ││DocGen    ││ChromaDB   │
│Sandbox  ││Sandbox   ││openpyxl ││docx/pptx ││RAG Search │
│         ││(net=none)││Formulas ││Templates ││Citations  │
└─────────┘└──────────┘└─────────┘└──────────┘└─────┬─────┘
                                                    │
                                            ┌───────▼──────┐
                                            │ Ollama Serve │
                                            │ (6GB VRAM)   │
                                            └──────────────┘
```

---

## 🛡️ Live Air-Gap Verification Command for Judges
To prove in real-time that no data leaves the machine during agent runs:
```bash
sudo tcpdump -i any not host 127.0.0.1 -n -c 20
```
An empty capture confirms zero outbound packets.
