# Self-Hosted Agentic AI Workbench for Air-Gapped Industrial Environments
### Requirements & Implementation Plan (v1.0)

> **How to use this document:** This is a build spec written to be handed directly to an engineering agent (human or AI). Section 3 is the definition of "done." Section 10 is the sprint-by-sprint task list. Everything else is architecture and rationale that section 10 depends on. Where a decision was made for you, the reasoning is included so it can be revisited if constraints change.

---

## 1. Problem Recap

Industrial/PSU/defence-linked/government environments produce large volumes of sensitive knowledge work (approval notes, board decks, engineering calculations, internal tool code, scanned drawings, inspection reports) that **cannot** go through cloud AI tools (Claude, Codex, etc.) because the underlying data — P&IDs, financials, vendor terms, unreleased designs, correspondence — is confidential. Today the choice is manual work or people quietly leaking data into public tools. Open-weight models are now good enough to close this gap, but no deployable, agent-capable, multi-model, air-gapped workbench exists that these users can actually work with.

**The build:** a self-hosted, air-gapped AI workbench on organization-owned GPU hardware that:
1. Runs multiple open-weight models simultaneously and **auto-selects** the right one per task.
2. Lets new open-weight models be **added without redesign**.
3. Acts as a genuine **agent** — plans, calls local tools, iterates, self-corrects.
4. Handles **multimodal** input — scanned PDFs, handwritten notes, drawings, photos — via on-device OCR/vision.
5. Produces **real deliverables** — Word/PPT/Excel files, verified code, shown-work calculations — not just chat replies.
6. Grounds itself in the org's own manuals/SOPs/correspondence via a **local knowledge base**.
7. Can **prove**, live, that zero data ever leaves the premises.

---

## 2. Goals, Non-Goals, Assumptions

**Goals**
- Working end-to-end demo on a single workstation/server with a mid-range GPU.
- Model-agnostic serving layer — adding a model is a config change, not a code change.
- Genuine multi-step agent loop with real tool use, not a single prompt-response wrapper.
- Verifiable network isolation, not just an assertion of it.

**Non-goals (for v1 / hackathon scope)**
- Fine-tuning or training any model from scratch.
- Full enterprise RBAC / multi-tenant access control (stub it, note as future work).
- Perfect P&ID symbol-level understanding — general vision-language models are good but not specialist CAD-symbol parsers yet; scope the demo drawing realistically and keep a human-in-the-loop confirmation step rather than promising fully autonomous drawing interpretation.
- High-availability / multi-node scaling — single-node deployment is the target.

**Assumptions made in this document (revisit if wrong)**
- Target OS: Linux (Ubuntu 22.04/24.04) — best driver, Docker, and isolation-tooling support.
- At least one NVIDIA GPU is available; exact VRAM is unknown at spec-writing time, so the plan is written to degrade gracefully (see §12).
- The team can install packages from PyPI/npm/Docker Hub **during development** on a network-connected machine, then move the built system to the air-gapped target. (Building the software doesn't have to happen air-gapped — running it in production/demo does.)
- "Modifying Ollama" in the problem statement is best satisfied by building a control-plane **on top of** Ollama's API rather than forking its Go source — see §5.1 for why.

---

## 3. Success Criteria — Definition of Done

Directly mapped to the problem statement's "Expected Solution." Do not consider the build finished until every box below can be demoed live:

- [ ] **Multi-model auto-selection**, shown across at least two different task types (e.g., a coding request routed to a coding model, a document-summary request routed to a general reasoning model), with the routing decision visibly logged.
- [ ] **End-to-end agentic task**: feed in a scanned inspection report → agent OCRs it → extracts key findings → drafts an approval note → saves it as a real `.docx` file.
- [ ] **Coding task**: agent writes code, executes it in a sandbox, verifies the result (tests pass / output correct), and the working code is a saved deliverable.
- [ ] **Multimodal task**: agent answers questions about or extracts structured data from an image/scanned document (drawing, handwritten note, or photo).
- [ ] **Air-gap proof**: a visible log or live network monitor demonstrating zero outbound network calls during the entire demo — this is graded as its own deliverable, not a footnote.
- [ ] **New model addition**: demonstrate adding a new open-weight model to the running system via config/registry only, no code redeploy.

---

## 4. High-Level Architecture

```
                          ┌───────────────────────────┐
                          │   Frontend (chat + task    │
                          │   timeline + file browser  │
                          │   + network monitor panel) │
                          └─────────────┬─────────────┘
                                        │ REST / WS
                          ┌─────────────▼─────────────┐
                          │      Orchestrator API      │
                          │        (FastAPI)           │
                          │  ┌───────────────────────┐ │
                          │  │   Task Router /        │ │
                          │  │   Model Selector       │ │
                          │  └──────────┬────────────┘ │
                          │  ┌──────────▼────────────┐ │
                          │  │   Agent Loop           │ │
                          │  │  (plan → act → observe │ │
                          │  │   → reflect → iterate) │ │
                          │  └──────────┬────────────┘ │
                          └─────────────┼─────────────┘
                                        │ tool calls
        ┌────────────┬─────────────────┼─────────────────┬────────────┐
        ▼            ▼                 ▼                 ▼            ▼
   ┌─────────┐  ┌───────────┐   ┌─────────────┐   ┌────────────┐ ┌──────────┐
   │  File   │  │  Code exec │   │ Spreadsheet │   │  RAG /     │ │ OCR /    │
   │  R/W    │  │  sandbox   │   │  tool       │   │  doc search│ │ Vision   │
   │  tool   │  │  (Docker,  │   │  (openpyxl) │   │  tool      │ │ tool     │
   │         │  │  net=none) │   │             │   │            │ │          │
   └─────────┘  └───────────┘   └─────────────┘   └─────┬──────┘ └────┬─────┘
                                                          │             │
                                                    ┌─────▼─────┐ ┌────▼─────┐
                                                    │ Vector DB │ │ Ingestion│
                                                    │ (Qdrant/  │ │ pipeline │
                                                    │  Chroma)  │ │ (loaders,│
                                                    └───────────┘ │ chunker) │
                                                                  └──────────┘
                          ┌─────────────────────────────┐
                          │   Model Serving Layer        │
                          │   Ollama (stock, unmodified) │
                          │   — multiple models resident  │
                          │   concurrently, one per task   │
                          │   family (reasoning / coding /│
                          │   vision / embedding)          │
                          └─────────────────────────────┘
                          ┌─────────────────────────────┐
                          │  Output Generation Layer      │
                          │  python-docx / python-pptx /  │
                          │  openpyxl → real deliverables │
                          └─────────────────────────────┘
                          ┌─────────────────────────────┐
                          │  Network Monitor + Audit Log  │
                          │  (proves the air-gap claim)    │
                          └─────────────────────────────┘

   Isolation boundary: everything above runs inside a network namespace/
   Docker network with no default route to the internet. See §5.8.
```

---

## 5. Component Deep-Dives

### 5.1 Model Serving Layer — use stock Ollama, don't fork it

Ollama already does the hard part of "multiple models, concurrently, model-agnostic":

- `OLLAMA_MAX_LOADED_MODELS` — how many different models can be resident in memory at once (auto-defaults to ~3× GPU count).
- `OLLAMA_NUM_PARALLEL` — concurrent requests per model.
- `OLLAMA_MAX_QUEUE` — backpressure instead of crashing under load.
- `OLLAMA_KEEP_ALIVE` — how long an idle model stays warm.
- Adding a new model is `ollama pull <model>` or a custom `Modelfile` + `ollama create` — no server restart, no code change.
- It already exposes a clean REST API (`/api/chat`, `/api/generate`, `/api/embeddings`, `/api/pull`, `/api/create`, `/api/ps`, `/api/tags`) including OpenAI-style tool/function calling for models that support it.

**Recommendation:** do not fork/modify Ollama's Go codebase. The "intelligence" the problem statement is asking for — auto-selecting the right model, adding new ones without redesign — belongs in a thin **control-plane service you build on top of Ollama**, not inside the model runtime itself. This is both less risky and directly satisfies "new models addable later without redesigning the system": adding a model becomes a registry entry, not a rebuild.

If, after building this, there's a genuine gap only a fork could fix (e.g., a scheduling behavior Ollama doesn't expose), revisit — but start here.

### 5.2 Task Router / Model Selector

Two-stage design:

1. **Classification** — a small, always-resident model (or a cheap embedding-similarity / keyword classifier if you want zero extra VRAM cost) tags the incoming task: `code_gen`, `code_review`, `doc_summarize`, `doc_draft`, `vision_ocr`, `spreadsheet_calc`, `general_qa`, `multi_step_plan`.
2. **Selection** — look up the tag in a **model registry** (a YAML/DB table, not code) that maps `capability tags → ollama model name → VRAM cost → context window`. Pick the best fit that also fits current available VRAM; fall back to a smaller model if the ideal one won't fit alongside what's already loaded.

Support a manual override (user/agent can pin a specific model) and **always log the routing decision** — this is one of the four demo requirements, so it must be visible, not just functional.

### 5.3 Agent Orchestrator — the actual "agent" part

This is the component that turns "a chatbot on local models" into "an agent," which is the core differentiator the problem statement is asking for.

- **Loop shape:** Plan → Act (tool call) → Observe (tool result) → Reflect (did that work? do I need to replan?) → repeat until done or blocked.
- **Framework choice:** build this as an explicit state graph rather than a single long prompt loop, so each step is inspectable and resumable — this matters both for reliability and for the "show your work" judging criterion. LangGraph (self-hostable, works against any OpenAI-compatible or Ollama endpoint, no cloud dependency) is a reasonable off-the-shelf choice; a hand-rolled state machine is equally valid if the team is short on time and wants full control. Either way, avoid frameworks that assume a cloud LLM API key.
- **Persistence:** task state (plan, steps taken, tool results, current status) persisted to SQLite/Postgres so a long task can be resumed, inspected, and shown in the UI as a live timeline ("step 3 of 5: extracting findings from inspection report").
- **Self-correction:** after each tool call, the agent checks the result against what it expected before moving on; on failure it retries (bounded, e.g. 2–3 attempts) or escalates to a human-in-the-loop checkpoint rather than looping forever or hallucinating success.

### 5.4 Tool Layer

| Tool | What it does | Key constraint |
|---|---|---|
| File read/write | Read/write within a scoped workspace directory | Path allowlist — agent cannot touch arbitrary filesystem paths |
| Code execution sandbox | Runs agent-written code and returns stdout/stderr/exit code | Docker container, `--network none`, CPU/mem/time limits, ephemeral (destroyed after run) |
| Spreadsheet tool | Reads/writes `.xlsx`, computes/verifies formulas | Use `openpyxl` (formulas stay live, not just static values, so the calc is auditable) |
| RAG / document search | Queries the local knowledge base | Returns source citations (doc name + section) so outputs are traceable |
| OCR / Vision | Extracts text/structure from images and scanned docs | Routed through the vision-capable model in the registry, not a separate hardcoded path |
| Output generation | Assembles a Word/PPT/Excel deliverable from structured content | Template-driven (see §5.7) so output looks like a real approval note / deck, not a raw text dump |

All tools should be exposed with a JSON-schema function-calling interface, since that's the format Ollama's tool-calling-capable models expect — this keeps the tool layer model-agnostic too.

### 5.5 Multimodal Ingestion Pipeline

```
file in → type detection
   ├── native-text PDF/DOCX  → direct text extraction (PyMuPDF / pdfplumber / python-docx)
   └── scanned image / handwriting / photo / drawing
            → vision-language model (via registry) for OCR + layout
            → normalized JSON: {raw_text, tables, key_value_fields, confidence}
```

For handwriting and scanned inspection reports, a general vision-language model (see §6) is usually sufficient. For dense structured documents (forms, tables), a dedicated OCR/document-parsing model tends to outperform a general VLM on pure text-extraction accuracy — worth benchmarking both against a real sample document early rather than assuming one is "the" answer.

For P&ID/engineering drawings specifically: treat this as the hardest input type. General VLMs can describe a drawing and often extract legible text labels, but symbol-level understanding (valve types, line codes) is a narrower, more specialized problem. Scope the demo drawing to something realistic but tractable, and design the agent to surface a confidence/"please confirm" step for drawing interpretation rather than presenting it as fully autonomous.

### 5.6 Knowledge Base / Local RAG

- **Vector DB:** Qdrant (richer metadata filtering, production-shaped) or Chroma (faster to stand up) — both self-hostable with zero external calls.
- **Embeddings:** served locally through Ollama's `/api/embeddings` (e.g. a BGE/Nomic/MixedBread-class open embedding model) — keeps embeddings on the same air-gapped serving layer as everything else, no separate embedding API.
- **Ingestion:** watch a folder for SOPs/manuals/correspondence → load → chunk (paragraph/semantic chunking, ~500–800 tokens with overlap) → embed → upsert with metadata (source, section, date). Re-run ingestion incrementally as new documents land.
- **Retrieval:** hybrid (keyword/BM25 + vector) matters here specifically because technical documents are full of part numbers, drawing codes, and jargon that pure embedding similarity sometimes misses. Return retrieved chunks with their source citation so agent output can point back to the exact manual/SOP it used.
- **Sensitivity tagging / access control:** out of scope for v1 functionally, but tag chunks with a sensitivity/department field now so role-based filtering can be added later without re-ingesting everything.

### 5.7 Output Generation Layer

- **Word (approval notes):** a `python-docx` template with fixed sections (Background / Findings / Recommendation / Sign-off) that the agent fills from its working memory — this reads as a real organizational artifact, not a chat transcript pasted into a doc.
- **PowerPoint:** `python-pptx` against a template deck for board-style summaries.
- **Excel:** `openpyxl`, with calculation steps kept as live formulas on one sheet and a summary on another, so a reviewer can audit the math rather than trust a single output number.
- **Code:** the verified script from the sandbox is itself a deliverable — save it to the workspace, don't just show it in chat.

### 5.8 Security & Air-Gap Enforcement (and *proof*)

This is graded as its own deliverable in the problem statement, so treat it as a first-class component, not an afterthought.

**Enforcement:**
- Entire stack (Ollama, orchestrator, vector DB, sandbox, frontend) runs inside a Docker Compose network with no default route out — either a bridge network with NAT/masquerade disabled, or host firewall rules (`iptables`/`ufw`) that `DROP` all outbound traffic except loopback/intra-cluster.
- Code-execution sandbox containers get `--network none` explicitly, in addition to the host-level rule — defense in depth.
- No component should have API keys or config pointing at any external endpoint (cloud model APIs, telemetry endpoints, package registries) at runtime. (Installing dependencies during development is fine; the deployed/demo instance should have no such config.)

**Proof (this is what actually convinces judges):**
- A live network-monitor panel in the UI — a small service (Python `psutil`/`scapy`, or `nethogs`/`iftop` piped into a simple dashboard) showing real-time bytes on the external interface, ideally at zero for the whole demo.
- In parallel, run `tcpdump -i <external-iface>` or Wireshark with a capture filter on the external interface during the demo — an empty capture is harder to argue with than a dashboard alone.
- Best-case setup: physically disconnect the demo machine from the venue network entirely (WiFi off, ethernet unplugged) *and* show the live capture/monitor as belt-and-suspenders. "We unplugged it and it still works" is the most convincing possible demo of the sovereignty claim.
- **Audit log:** every model call, tool call, and file write logged locally (timestamp, model used, tokens in/out, tool name, result) — supports both the air-gap story and an "explain what the agent did and why" story for judges.

### 5.9 Frontend

Chat panel + agent task timeline (live steps/tool calls/status) + deliverables/file browser + network monitor panel, all talking only to the local orchestrator API.

Given hackathon time constraints, **Streamlit or Gradio will get a working demo UI up far faster** than a custom React app, and is a perfectly legitimate choice for a workbench like this. Only invest in a custom frontend if there's spare time and frontend bandwidth after the core agent/routing/tooling work is solid — a good demo of a mediocre UI beats a great UI wrapped around a broken agent loop.

---

## 6. Recommended Model Lineup (verify at build time — this space moves fast)

These are current, reasonable starting points as of the time of writing. Re-check availability, benchmarks, and — importantly for a defence-linked deployment — **license terms** before finalizing, since licenses vary in whether they restrict government/military use. MIT/Apache-2.0-licensed options are the least likely to raise a compliance question; some other model families carry community licenses with use restrictions worth reading closely.

| Task type | If large GPU capacity available | Fallback (single mid-range GPU, ~24GB) | Notes |
|---|---|---|---|
| General reasoning / planning | Qwen3-class MoE (235B-A22B), DeepSeek-V3.2/V4 | Qwen3 30B-A3B, Gemma 3 27B, Phi-4 (dense, ~8GB Q4) | MoE models only activate a fraction of total params — check *active*-param VRAM math, not total param count |
| Coding | DeepSeek-Coder-class, Qwen-Coder-class | Qwen2.5/3-Coder 14B–32B (Q4) | Confirm the model's Ollama chat template actually supports tool/function calling before committing to it as the coding-agent model |
| Vision / OCR / drawings | Qwen2.5/3-VL 72B, GLM-4.5V-class | Qwen2.5-VL 7B, or a dedicated OCR model (PaddleOCR-VL / DeepSeek-OCR, ~3B) | Dedicated OCR models often beat general VLMs on raw text-extraction accuracy; general VLMs are better at "describe/reason about this drawing" |
| Embeddings | Any BGE-M3 / Nomic / MixedBread-class embedding model | Same — embedding models are small | Served via Ollama `/api/embeddings`, keep it resident alongside the other models |
| Router/classifier | Small 1–3B instruct model, or rules/embedding-similarity | Same | Should be near-instant and always resident — this runs on every single request |

**Action item for the team:** before locking in a model list, run a 30-minute bake-off on the actual target GPU — pull 2–3 candidates per row, check load time, VRAM footprint when 2–3 models are resident together, and tool-calling reliability. Don't pick models off a leaderboard alone.

---

## 7. Tech Stack Summary

| Layer | Choice | Why |
|---|---|---|
| Model runtime | Ollama (stock) | Multi-model concurrency, hot model add, REST API, tool calling — already built |
| Control plane / orchestrator | Python + FastAPI | Fast to build, huge ecosystem, easy to wrap any tool as an endpoint |
| Agent framework | LangGraph, or a hand-rolled state machine | Explicit, inspectable steps; no cloud dependency |
| Vector DB | Qdrant (or Chroma for speed) | Self-hostable, metadata filtering, zero external calls |
| Relational/audit store | SQLite (or Postgres if multi-user) | Task state, audit log |
| Sandbox | Docker, `--network none`, resource limits | Simple, well-understood isolation; upgrade to gVisor/Firecracker later if needed |
| OCR/Vision | Served via Ollama + optional dedicated OCR library (PaddleOCR) | Model-agnostic vision, specialist OCR fallback |
| Document generation | `python-docx`, `python-pptx`, `openpyxl` | Real, editable deliverables |
| Frontend | Streamlit/Gradio (MVP) → React/Next.js (stretch) | Speed first, polish later |
| Network proof | `tcpdump`/Wireshark + custom `psutil`/`scapy` dashboard | Live, undeniable evidence of the air-gap |
| Containerization | Docker Compose, isolated bridge network + host firewall | Reproducible, easy to lock down |
| OS | Ubuntu 22.04/24.04 | GPU driver, Docker, isolation tooling all mature here |

---

## 8. Repository Structure

```
ai-workbench/
├── docker-compose.yml
├── .env.example
├── orchestrator/
│   ├── main.py
│   ├── router/
│   │   ├── registry.yaml        # model capability registry — edit this to add a model
│   │   └── classifier.py
│   ├── agent/
│   │   ├── graph.py              # plan → act → observe → reflect loop
│   │   └── memory.py
│   ├── tools/
│   │   ├── files.py
│   │   ├── sandbox.py
│   │   ├── spreadsheet.py
│   │   ├── docgen.py
│   │   ├── rag_search.py
│   │   └── vision_ocr.py
│   ├── ingestion/
│   │   ├── loaders.py
│   │   └── ocr_pipeline.py
│   ├── rag/
│   │   ├── embed.py
│   │   └── vector_store.py
│   └── audit/
│       └── logger.py
├── sandbox-runner/                # Dockerfile for the isolated code-exec image
├── network-monitor/                # egress-proof service + dashboard
├── frontend/                       # Streamlit/Gradio or React app
├── models/
│   └── Modelfiles/                 # custom Modelfiles for quantized/tuned variants
├── data/
│   ├── knowledge_base/             # watched folder — drop SOPs/manuals here
│   └── workspace/                  # agent scratch space + deliverables land here
└── docs/
    └── this-file.md
```

---

## 9. Internal API Contracts (orchestrator ↔ frontend ↔ tools)

| Endpoint | Purpose |
|---|---|
| `POST /v1/task` | `{prompt, attachments[]}` → `{task_id}` — kicks off an agent run |
| `GET /v1/task/{id}` | Current status, step trace, active tool call — powers the live timeline |
| `POST /v1/task/{id}/approve` | Human-in-the-loop resume for a checkpointed step |
| `GET /v1/models` | Registry contents + which models are currently loaded |
| `POST /v1/models/register` | Add a model: `{name, ollama_tag, capabilities[], vram_gb, context_window}` — no redeploy required |
| `POST /v1/tools/{tool_name}/invoke` | Internal — called by the agent loop, not the frontend directly |
| `GET /v1/network-status` | Live egress byte counters for the network monitor panel |

---

## 10. Implementation Phases

Each phase lists what "done" looks like. Sizes are relative effort, not calendar time — fit them to your actual timeline.

### Phase 0 — Infra Setup
- [ ] Ubuntu box with GPU driver + CUDA verified (`nvidia-smi` works)
- [ ] Docker + Docker Compose + NVIDIA container toolkit installed
- [ ] Ollama installed, `OLLAMA_MAX_LOADED_MODELS`/`OLLAMA_NUM_PARALLEL`/`OLLAMA_KEEP_ALIVE` tuned for your VRAM
- [ ] 2–3 candidate models per task type (§6) pulled and smoke-tested individually
- **Done when:** you can `curl` the Ollama API and get a response from at least one model of each type (reasoning, coding, vision, embedding).

### Phase 1 — Model Registry & Router
- [ ] `registry.yaml` schema defined (name, tag, capabilities, vram_gb, context_window)
- [ ] Classifier that tags an incoming request with a task type
- [ ] Router that resolves task type → best-fit registered model, with VRAM-aware fallback
- [ ] Routing decisions logged and queryable
- **Done when:** two different task-type prompts visibly route to two different models, and adding a third model to `registry.yaml` (no code change) makes it selectable.

### Phase 2 — Agent Orchestration Core
- [ ] Plan → act → observe → reflect loop implemented
- [ ] Task state persisted (SQLite), resumable
- [ ] At least the file read/write tool wired end-to-end
- **Done when:** a multi-step prompt ("read this file, summarize it, save the summary") completes without a human intervening between steps, and the step trace is inspectable.

### Phase 3 — Tool Layer Expansion
- [ ] Code execution sandbox (Docker, `--network none`, resource limits)
- [ ] Spreadsheet tool (`openpyxl` read/write/formula)
- [ ] Output generation tool (`python-docx`/`python-pptx`)
- **Done when:** the agent can write code, run it in the sandbox, and separately produce a Word file from structured content, both via tool calls (not hardcoded shortcuts).

### Phase 4 — Multimodal Ingestion
- [ ] Type detection (native-text vs scanned/image)
- [ ] Vision-model OCR path wired through the router (not hardcoded to one model)
- [ ] Normalized extraction output (`raw_text`, `tables`, `key_value_fields`, `confidence`)
- **Done when:** a scanned inspection report produces structured extracted text the agent can reason over.

### Phase 5 — Local Knowledge Base / RAG
- [ ] Vector DB stood up (Qdrant/Chroma)
- [ ] Ingestion pipeline: watch folder → load → chunk → embed → upsert
- [ ] RAG search tool returning chunks with source citations
- [ ] Hybrid (keyword + vector) retrieval
- **Done when:** dropping a new SOP into the watched folder makes it retrievable and cited in an agent answer without a restart.

### Phase 6 — Security, Air-Gap Enforcement & Proof
- [ ] Docker network / firewall rules blocking all outbound traffic except intra-cluster
- [ ] Sandbox containers confirmed `--network none`
- [ ] Network monitor service + dashboard panel built
- [ ] Audit logger recording every model/tool call
- **Done when:** you can run the full demo with `tcpdump` capturing the external interface and the capture file is empty at the end.

### Phase 7 — Frontend & Demo Polish
- [ ] Chat + live task timeline
- [ ] Deliverables/file browser
- [ ] Network monitor panel wired to the live status endpoint
- [ ] End-to-end rehearsal of all four demo scenarios (§11) back-to-back
- **Done when:** someone who didn't build the system can walk through the demo checklist in §3 unaided.

---

## 11. End-to-End Demo Script (map straight to §3)

1. **Routing demo:** submit a coding prompt and a document-summary prompt back to back. Show the router log picking a different model for each, with the reasoning ("classified as `code_gen` → routed to `<coding model>`").
2. **Agentic task:** upload a scanned inspection report. Watch the timeline: OCR → extract findings → draft approval note → save `.docx`. Open the resulting Word file.
3. **Coding task:** ask for a script (e.g., validate a CSV of inspection readings against tolerance limits). Show it running in the sandbox with visible stdout, and the saved script as a deliverable.
4. **Multimodal task:** feed a photo of a handwritten note or a drawing; ask a question about it or ask for structured extraction.
5. **Air-gap proof:** run the whole thing with the network monitor panel and a live `tcpdump`/Wireshark capture visible throughout. End by showing the capture is empty.
6. **New-model demo:** add a new entry to `registry.yaml`, `ollama pull` it, and show it becoming selectable — no restart, no redeploy.

---

## 12. Hardware Sizing & Fallback Plan

- **Ideal:** multi-GPU server (e.g., 2–4× 80GB-class GPUs) — runs 100B+-class MoE models comfortably with headroom for a resident vision model and embedding model at the same time.
- **Realistic hackathon venue:** a single workstation with one consumer/prosumer GPU (24GB class). Plan around Q4/Q5-quantized 14B–32B dense or 30B-class MoE models per row 2 of the table in §6 — this is explicitly allowed by the problem statement itself.
- Test early whether your chosen models can be resident **simultaneously** at the quantization level you're using — the multi-model concurrency demo requires at least two models loaded at once (e.g., a reasoning model + a vision model, or reasoning + embedding), so VRAM budgeting has to account for that, not just the single-largest-model case.

---

## 13. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| VRAM contention when multiple models are resident | Registry-declared VRAM budgets, `OLLAMA_MAX_LOADED_MODELS` tuning, graceful queuing instead of OOM crashes |
| Inconsistent tool-calling support across open-weight models | Standardize on one function-calling schema; verify each candidate model's Ollama chat template actually supports it before committing |
| Weak P&ID/drawing symbol understanding | Scope the demo drawing realistically; keep a human-confirmation step rather than claiming full autonomy there |
| Sandbox escape or accidental external call from generated code | Hard `--network none` on sandbox containers, plus host-level firewall as a second layer |
| Model license restricts government/defence use | Explicitly check each candidate model's license before final selection; prefer MIT/Apache-2.0 where the use case is sensitive |
| Live multi-step demo fails on stage | Rehearse the exact demo script end-to-end multiple times; keep a pre-recorded/cached "golden path" run as a fallback while still attempting live |

---

## 14. Air-Gap Verification Checklist (run before the demo, every time)

- [ ] `iptables -L -n` / `ufw status` shows outbound traffic blocked except intra-cluster
- [ ] `docker network inspect <network>` confirms no external gateway/NAT
- [ ] Sandbox container launched with `docker inspect` confirming `NetworkMode: none`
- [ ] `tcpdump -i <external-iface>` running and captured to a file for the full demo duration
- [ ] No DNS queries observed leaving the host during the demo
- [ ] Audit log shows every model/tool call resolved to a local endpoint (`127.0.0.1`/intra-cluster IP), none external

---

## 15. Open Questions for the Team

- Exact GPU inventory available for the build/demo (this determines the final row-2-vs-row-1 model picks in §6).
- Does the demo need to support more than one concurrent user, or is single-user sufficient for judging?
- Is any level of role-based access control actually required for the demo, or is it purely a "future work" mention?
- Which specific document types (languages, formats, handwriting styles) should the multimodal demo be tuned against — pick the most representative real example now rather than late.
- What's the actual deadline/timeline driving the phase sequencing in §10?

---

## 16. Appendix

### Sample `registry.yaml`
```yaml
models:
  - name: reasoning-primary
    ollama_tag: qwen3:30b-a3b
    capabilities: [general_qa, doc_summarize, doc_draft, multi_step_plan]
    vram_gb: 20
    context_window: 128000

  - name: coding-primary
    ollama_tag: qwen2.5-coder:32b
    capabilities: [code_gen, code_review]
    vram_gb: 20
    context_window: 32000

  - name: vision-primary
    ollama_tag: qwen2.5-vl:7b
    capabilities: [vision_ocr]
    vram_gb: 8
    context_window: 32000

  - name: embeddings
    ollama_tag: bge-m3
    capabilities: [embedding]
    vram_gb: 2
```

### Sample environment variables
```
OLLAMA_MAX_LOADED_MODELS=3
OLLAMA_NUM_PARALLEL=2
OLLAMA_MAX_QUEUE=512
OLLAMA_KEEP_ALIVE=30m
```

### Sample sandbox run invocation (concept)
```bash
docker run --rm \
  --network none \
  --memory=2g --cpus=1 \
  --read-only \
  -v /data/workspace/task_123:/work:rw \
  sandbox-runner:latest python /work/script.py
```
