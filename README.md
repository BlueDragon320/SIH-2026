# Self-Hosted Agentic AI Workbench for Air-Gapped Industrial & Defence Environments

[![Air-Gap Certified](https://img.shields.io/badge/Air--Gap-100%25%20Verified%20Zero%20Egress-success)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware](https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203060%20(6GB%20VRAM)-blue)](#)
[![Model Serving](https://img.shields.io/badge/Runtime-Stock%20Ollama-orange)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%7C%20Vite%20%7C%20Tailwind-61dafb)](#)

A fully self-hosted, air-gapped agentic AI workbench engineered for industrial, public sector undertakings (PSUs), and defence environments where engineering designs, telemetry, financial data, and approval notes **must never leave physical premises**.

---

## 🚀 Key Capabilities

1. **Multi-Model Auto-Routing & Dynamic Model Registration**:
   - Classifies user intents into coding, document drafting, spreadsheet modeling, RAG document search, and visual inspection.
   - Automatically routes tasks to optimal quantized local models (`qwen2.5-coder:3b`, `moondream`, `nomic-embed-text`) tailored for memory-constrained hardware (6GB VRAM).
   - Supports hot dynamic model registration without server restarts.

2. **Autonomous Agent Loop (Plan → Act → Observe → Reflect → Self-Correct)**:
   - Autonomous multi-step execution breakdown with automatic validation and error self-correction.
   - Persists step telemetry and live execution state to SQLite with inspectable execution timelines.

3. **Secure Sandboxed Tool Execution & Dynamic Visual Chart Capture**:
   - **Kernel-Level Sandboxing**: Sandboxed Python execution using Linux namespaces (`bwrap --unshare-net`) with guaranteed zero external network access.
   - **Dynamic Chart Extraction**: Visualizations generated via `matplotlib` and `seaborn` during sandboxed code execution are automatically captured, routed to the Artifact Canvas, and displayed with interactive pan, zoom, full-resolution downloads, and multi-chart switcher tabs.
   - **Spreadsheet Generation**: Produces `.xlsx` workbooks with live mathematical formulas (`=SUM()`, `=AVERAGE()`).
   - **Enterprise Document Drafting**: Generates formal Word Approval Notes (`.docx`) and Executive PowerPoint Decks (`.pptx`).

4. **Strict Chat-Scoped Context & File Isolation**:
   - Each chat session operates in complete contextual containment.
   - The agent strictly processes and references only the files explicitly attached to that specific conversation thread, eliminating cross-session data leakage.

5. **Real-Time Hardware Telemetry & Inference Stopwatch**:
   - Dynamically queries on-device hardware (NVIDIA NVML / PyTorch CUDA) to display the active GPU model name, temperature, and live VRAM consumption.
   - Built-in live stopwatch timer next to model execution headers displays active processing time during inference and stops automatically on completion.

6. **Enterprise Role-Based Access Control (RBAC)**:
   - Built-in authentication supporting Administrators and Standard Users.
   - Admin dashboard for monitoring active sessions, login history, and user activity.
   - Dynamic project-root relative path resolution for seed account initialization.

7. **Multimodal Ingestion & Local RAG**:
   - On-device Vision OCR (`moondream`) for scanned inspection reports, blueprints, and diagrams.
   - Air-gapped ChromaDB vector store with hybrid (BM25 keyword + cosine semantic) search and source citation tracking.
   - Automatic background Folder Watcher (`folder_watcher.py`) that monitors the knowledge base and ingests incoming files in real time.

8. **Dual-Theme High Contrast Design**:
   - Complete Light and Dark theme support with contrast-compliant UI elements, readable dialogs, and adaptive action menus.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│               Modern React Web Application (Port 5173)                 │
│  (Chat Thread | Artifacts Canvas | Egress Meter | Admin Dashboard)     │
│      ├── Reverse Proxy `/api`    → http://127.0.0.1:8000               │
│      └── Reverse Proxy `/ollama` → http://127.0.0.1:11434              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ REST / SSE
┌───────────────────────────────────▼────────────────────────────────────┐
│             FastAPI Control Orchestrator (Port 8000)                   │
│  ┌────────────────────────┐  ┌──────────────────────────────────────┐  │
│  │ Task Router & Registry │  │ Agent State Graph (LangGraph-style)  │  │
│  ├────────────────────────┤  ├──────────────────────────────────────┤  │
│  │ Folder Watcher (KB)    │  │ Role-Based Auth & Session DB         │  │
│  └────────────────────────┘  └──────────────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Tool Execution Layer
   ┌────────────┬───────────┬───────┴───┬────────────┬───────────┐
   ▼            ▼           ▼           ▼            ▼           ▼
┌─────────┐┌──────────┐┌─────────┐┌──────────┐┌───────────┐┌───────────┐
│File R/W ││bwrap Code││Excel    ││DocGen    ││ChromaDB   ││Vision OCR │
│Sandbox  ││Sandbox   ││openpyxl ││docx/pptx ││Vector RAG ││moondream  │
│Allowlist││(net=none)││Formulas ││Templates ││Hybrid BM25││Blueprints │
└─────────┘└──────────┘└─────────┘└──────────┘└─────┬─────┘└─────┬─────┘
                                                    │           │
                                            ┌───────▼───────────▼──────┐
                                            │ Local Ollama Serve       │
                                            │ (127.0.0.1:11434)        │
                                            └──────────────────────────┘
```

---

## 📦 Quick Start Guide

### Prerequisites
- **Operating System**: Linux (Ubuntu 22.04+ or Debian-based distribution recommended)
- **Hardware**: NVIDIA GPU with 6GB+ VRAM (RTX 3060 or equivalent recommended)
- **Software**:
  - Python 3.10+ (with `venv`)
  - Node.js 18+ and `npm`
  - Bubblewrap (`sudo apt install bubblewrap`)
  - Ollama runtime (`https://ollama.com`)

### 1. Start All Workbench Services
Execute the master startup script from the project root:
```bash
./start_workbench.sh
```

This launches the three air-gapped services:
1. **Ollama LLM Serving Daemon**: `http://127.0.0.1:11434`
2. **FastAPI Control-Plane Orchestrator**: `http://127.0.0.1:8000`
3. **React Web UI (Vite Dev Server)**: `http://127.0.0.1:5173`

To stop all services cleanly at any time:
```bash
./start_workbench.sh --stop
```

### 2. Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:5173
```

### 3. Default User Credentials
The system initializes two default seed accounts on first startup:

| Username | Password | Role | Description |
| :--- | :--- | :--- | :--- |
| **`admin`** | `admin123` | Administrator | Full administrative dashboard, user management, and audit inspection |
| **`user1`** | `user123` | Operator | Standard workbench user for chat, file analysis, and agent execution |

---

## 🧪 Verification & Testing

### 1. Definition-of-Done (DoD) Comprehensive Verification
Run the end-to-end automated verification script covering all core requirements:
```bash
.venv/bin/python verify_all.py
```

### 2. Unit & Integration Test Suite
Execute the full test suite (API endpoints, authentication, folder watcher, and tools):
```bash
PYTHONPATH=. .venv/bin/pytest tests/test_auth_api.py tests/test_spec_enhancements.py -v
```

### 3. Real-Time Hardware Air-Gap Verification (Zero-Egress Proof)
To independently verify in real time that zero network egress occurs during model inference and agent execution:
```bash
sudo tcpdump -i any not host 127.0.0.1 -n -c 20
```
*(An empty capture proves 100% air-gapped operation with zero packets leaving the host.)*

---

## ⚖️ Open Source Licensing & Legal Attributions

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for complete terms. You are free to use, modify, distribute, and publish this software.

### Upstream Open-Source Acknowledgements
This workbench integrates and builds upon key open-source software and model architectures. We gratefully acknowledge:

- **[Ollama](https://github.com/ollama/ollama)** — MIT License, Copyright (c) Ollama. Used as the local model serving runtime for LLMs and VLMs.
- **[FastAPI](https://github.com/fastapi/fastapi)** — MIT License, Copyright (c) 2018 Sebastián Ramírez.
- **[React](https://github.com/facebook/react)** — MIT License, Copyright (c) Meta Platforms, Inc. and affiliates.
- **[Vite](https://github.com/vitejs/vite)** — MIT License, Copyright (c) 2019-present Evan You & Vite Contributors.
- **[ChromaDB](https://github.com/chroma-core/chroma)** — Apache License 2.0, Copyright (c) Chroma.
- **[Bubblewrap](https://github.com/containers/bubblewrap)** — LGPL-2.0+, Copyright (c) Bubblewrap contributors.
- **Local Open Model Weights**:
  - `Qwen2.5-Coder` (Alibaba Cloud / Apache 2.0 / Qwen Community License)
  - `Moondream` (Apache 2.0)
  - `Nomic Embed Text` (Nomic AI / Apache 2.0)

For full licensing notices of dependencies, refer to the [NOTICE](NOTICE) file.
