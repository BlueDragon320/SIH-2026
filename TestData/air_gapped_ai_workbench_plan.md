# Sovereign AI Workbench for Industrial & Government Use
## Requirements, Architecture & Implementation Plan

**Status:** Draft for build-out
**Audience:** Implementation agent / engineering team
**Target environment:** Fully air-gapped, on-premises GPU server (production) with a demo/dev path on a single 6GB-VRAM laptop GPU
**Demo hardware baseline used throughout this document:** NVIDIA RTX 4060 Laptop GPU, 6 GB VRAM, one 7B-parameter open-weight model quantized to ~5 GB

---

## 1. Problem Statement (restated)

Refineries, PSUs, defence-linked manufacturing units and government offices generate large volumes of routine but sensitive knowledge work: approval notes, board presentations, engineering calculations, internal tool code, review of scanned drawings and inspection reports. This data — P&IDs, financials, vendor negotiations, unreleased designs, internal correspondence, confidential business strategy — cannot legally or contractually leave the premises. Today, staff either lose the productivity gains of AI assistance entirely, or (against policy) paste confidential material into public cloud tools like Claude or Codex.

Open-weight reasoning models are now capable enough that a genuinely useful assistant can be built on them and run entirely on an organization's own hardware. **Nothing deployable and easy to actually use exists today for this segment.** This document specifies that system.

## 2. Goals

1. **Zero egress.** Nothing — no telemetry, no update check, no model download at runtime, no API call — leaves the network boundary. This is a hard requirement, not a configuration option.
2. **Model-agnostic backend.** The system must run multiple open-weight models concurrently and route each task to the model best suited for it. Adding a new open-weight model must be a configuration change, not a code change.
3. **Real agency.** The assistant plans multi-step work, calls local tools (file I/O, sandboxed code execution, spreadsheet manipulation, internal document search), observes results, and iterates — it does not just answer once and stop.
4. **Multimodal by default.** Scanned PDFs, handwritten notes, engineering drawings, and photographs must be first-class inputs via on-device OCR and vision-language models.
5. **Deliverables, not chat.** Output should be an approval note as a `.docx`, a board deck as `.pptx`, a cost model as `.xlsx`, a script that has actually been run and verified, a calculation with every step shown — not a chat bubble the user has to manually transcribe.
6. **Grounded in the organization's own knowledge.** A local knowledge base connector indexes manuals, SOPs, drawings, and past correspondence, and every answer that depends on institutional knowledge must cite the internal source it came from.
7. **Provable sovereignty.** The "no data leaves the premises" claim must be demonstrable via logs and a live network monitor, not just asserted.

## 3. Non-Goals (for this phase)

- Training or fine-tuning foundation models from scratch. We consume open-weight models as-is (optionally with light LoRA fine-tuning later — see §12).
- Multi-user enterprise identity/SSO integration. The demo/first deployment assumes a single trusted workstation or a small trusted user group; RBAC hooks are stubbed but not fully built.
- Real-time control-system integration (DCS/SCADA read-write). The workbench consumes *reports about* plant data (CSVs, exports, scanned logs) — it does not connect to live control networks. This is itself a safety/air-gap boundary, not just a scoping choice.
- Guaranteeing dimensional accuracy of vision-model-read engineering drawings for construction use. The vision pipeline assists human review; it does not replace a certified engineer's sign-off.

## 4. Success Criteria (what "done" looks like for the demo)

These map directly to the "Expected Solution" in the problem statement. Each must be demonstrable end-to-end on the target hardware:

| # | Demonstration | Proves |
|---|---|---|
| 1 | Submit a coding task and a document-summary task in the same session; logs show two different backend models were selected automatically | Model auto-selection across ≥2 task types |
| 2 | Feed a scanned inspection report image/PDF; the agent OCRs it, extracts key findings, and produces a Word approval note as a file | End-to-end agentic task, multimodal input, real deliverable output |
| 3 | Give a coding request; the agent writes code, executes it in a sandbox, observes the result (including an error and a fix cycle), and reports back with the verified output | Agentic iteration + sandboxed code execution |
| 4 | Feed an engineering drawing (P&ID-style image) and ask a question that requires reading tags/lines off it | Multimodal / vision understanding |
| 5 | A visible network monitor (or reviewed logs) shows zero outbound connections during all of the above | Sovereign / air-gapped claim, proven not stated |

## 5. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Air-Gapped Boundary                         │
│                                                                       │
│  ┌───────────────┐      ┌────────────────────────────────────────┐  │
│  │   Web UI /     │      │           Orchestrator / Agent          │  │
│  │  Chat Client   │◄────►│   (planning loop, tool calling, state)  │  │
│  └───────────────┘      └───────────────┬────────────────────────┘  │
│                                          │                            │
│                    ┌─────────────────────┼─────────────────────┐     │
│                    ▼                     ▼                     ▼     │
│           ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐│
│           │  Model Router    │  │   Tool Layer      │  │  Ingestion   ││
│           │ (task→model map) │  │ - file read/write  │  │  Pipeline    ││
│           └───────┬──────────┘  │ - code sandbox     │  │ - OCR        ││
│                    │             │ - spreadsheet ops   │  │ - Vision-LM ││
│      ┌─────────────┼──────────┐ │ - doc search (RAG) │  │ - chunker    ││
│      ▼             ▼          ▼ └──────────────────┘  └──────┬───────┘│
│ ┌─────────┐  ┌──────────┐ ┌────────┐                          │       │
│ │ Model A  │  │ Model B  │ │Model C │      ┌───────────────────▼─────┐│
│ │ (chat/   │  │ (code)   │ │(vision)│      │   Local Vector Store /   ││
│ │ reasoning)│  │          │ │        │      │   Knowledge Base (RAG)  ││
│ └─────────┘  └──────────┘ └────────┘      └──────────────────────────┘│
│                                                                       │
│           ┌───────────────────────────────────────────────┐          │
│           │        Output Builders (docx / pptx / xlsx)     │          │
│           └───────────────────────────────────────────────┘          │
│                                                                       │
│           ┌───────────────────────────────────────────────┐          │
│           │  Network Egress Monitor / Firewall (deny-all,  │          │
│           │  logged, visible in a live dashboard)           │          │
│           └───────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

Every box above runs on-premises. No box makes an outbound call across the boundary at any point. The egress monitor is not decorative — it is the mechanism that proves this in the demo.

## 6. Hardware Tiers

| Tier | Hardware | Model config | Use |
|---|---|---|---|
| **Dev / demo** | Single laptop, RTX 4060 6GB VRAM, 16–32GB system RAM | One 7B model, GGUF Q4_K_M quantization (~4.5–5GB), 4–8K context | Local development, portable demos at a venue without a server rack |
| **Pilot** | Single workstation/server, 1× RTX 4090/A6000 (24–48GB VRAM) | 2–3 models resident simultaneously: a ~13–34B general model, a code-specialist model, a 7B VLM for vision | Small department pilot (e.g., one plant unit) |
| **Production** | On-prem GPU server, multi-GPU (e.g., 4–8× A100/H100, or equivalent) | 70B–120B-class MoE or dense reasoning model, a dedicated coding model, a dedicated VLM, all served concurrently with room for a second replica for HA | Org-wide deployment across a refinery/PSU site |

**Design constraint driven by the demo tier:** everything in this document must degrade gracefully to the 6GB/7B tier. Concretely this means:
- Default context window capped at **4096 tokens** on the demo tier (raise to 8K only if KV-cache headroom is confirmed empirically — see §7.3).
- Only **one** large generative model loaded in VRAM at a time on the demo tier; a second, much smaller model (an OCR/layout model or a tiny classifier) can share the remaining ~1GB.
- The **vision** and **generation** roles are time-sliced on one GPU on the demo tier (load/unload) rather than co-resident, unless a quantized VLM small enough to coexist is used (see §9.1 sizing table).
- All of this is config-driven (see §7), so moving to Pilot/Production tier is a config change (raise concurrency, point at bigger models), not a rewrite.

## 7. Model Router (multi-model, pluggable)

### 7.1 Principle

The router is a **thin, declarative layer**. It never hardcodes model names in application logic. All model knowledge lives in one file: `config/models.yaml`. Adding a model = adding a YAML block + dropping the weights in the model directory. No redesign, no redeploy of the orchestrator code.

### 7.2 `config/models.yaml` (illustrative)

```yaml
models:
  general-reasoning:
    engine: llama.cpp        # or vllm, ollama — see §7.4
    weights: models/qwen2.5-7b-instruct-q4_k_m.gguf
    context_window: 4096
    capabilities: [chat, summarization, document_qa, planning]
    vram_estimate_gb: 4.8
    priority: default

  code-specialist:
    engine: llama.cpp
    weights: models/qwen2.5-coder-7b-instruct-q4_k_m.gguf
    context_window: 8192
    capabilities: [code_generation, code_review, debugging]
    vram_estimate_gb: 4.9
    priority: preferred_for: [code_generation, code_review, debugging]

  vision:
    engine: llama.cpp
    weights: models/qwen2-vl-7b-instruct-q4_k_m.gguf
    context_window: 4096
    capabilities: [image_understanding, drawing_reading, ocr_assist]
    vram_estimate_gb: 5.2
    priority: preferred_for: [image_understanding, drawing_reading]

  embeddings:
    engine: llama.cpp
    weights: models/bge-small-en-v1.5-q8_0.gguf
    capabilities: [embedding]
    vram_estimate_gb: 0.3

routing:
  # Rule-based first pass (cheap, deterministic, auditable).
  # Falls back to a lightweight classifier prompt against
  # `general-reasoning` only when no rule matches.
  rules:
    - if_contains: ["```", "def ", "function ", "traceback", "stack trace", "compile error"]
      route_to: code-specialist
    - if_attachment_type: [png, jpg, jpeg, tiff]
      route_to: vision
    - if_attachment_type: [pdf]
      condition: "pdf_is_scanned == true"
      route_to: vision
    - default: general-reasoning

concurrency:
  demo_tier:
    max_resident_models: 1
    swap_strategy: lru        # unload least-recently-used model when VRAM is needed
  pilot_tier:
    max_resident_models: 3
    swap_strategy: none       # all resident, enough VRAM
```

### 7.3 Router behavior requirements

1. **Deterministic rules first, classifier fallback second.** Rules (file type, code fences, error strings, explicit user tool selection) are cheap and auditable — an inspector should be able to read the log and see *why* a task went to a given model. Only ambiguous free-text tasks fall through to a one-shot classification prompt.
2. **Every routing decision is logged** with: input task hash, matched rule (or classifier verdict), model selected, VRAM state before/after. This log is itself demo evidence for Success Criterion #1.
3. **Swap latency must be measured and shown to the user** (a short "loading code-specialist model…" indicator) on the demo tier, since model swaps on a 6GB card take real time (typically 3–8 seconds for a 5GB GGUF from local NVMe). This is an honest UX choice, not a thing to hide.
4. **New model onboarding checklist** (this should be literally followed when adding a model): drop weights in `models/`, add a YAML block, add capability tags, run `scripts/validate_model_config.py` (loads the model once, checks it responds, measures actual VRAM footprint vs. the estimate, writes the measured number back into the YAML), done.

### 7.4 Serving engine choice

- **Demo/Pilot tier:** `llama.cpp` (via its OpenAI-compatible server mode) or **Ollama** (which wraps llama.cpp) — both run GGUF-quantized models with minimal VRAM overhead, support model swapping, and run entirely offline once models are on disk. Recommended for the 6GB tier because of the lowest VRAM overhead per model.
- **Production tier:** **vLLM** for the general-reasoning and code models (higher throughput, continuous batching, tensor-parallelism across multiple GPUs), keep llama.cpp/Ollama available as a fallback path for smaller auxiliary models. This is a deployment-config change; the router's YAML `engine:` field is exactly the abstraction that makes this swap non-invasive.

## 8. Agent Core (planning, tool use, iteration)

### 8.1 Loop design

Use a **ReAct-style loop** (Reason → Act → Observe → repeat) with an explicit, inspectable scratchpad:

```
1. Receive task + context (attachments, retrieved KB chunks, prior turns)
2. PLAN: model produces a short numbered plan (max ~6 steps) before acting
3. ACT: model emits one tool call (structured JSON per the tool schema)
4. OBSERVE: orchestrator executes the tool call, captures stdout/stderr/result,
   truncates if huge, appends to scratchpad
5. REFLECT: model checks observation against the plan step; on failure,
   revise the plan (max 3 retries per step before surfacing to the user)
6. Repeat until plan complete or max_iterations (default 12) reached
7. FINALIZE: produce the actual deliverable file(s) + a short natural-language summary
```

- Steps 2–6 all happen against whichever model the router assigned for that sub-task — a single agent run can call **different models for different steps** (e.g., vision model to read a drawing in step 2, general model to draft the note in step 4, code model if a calculation script is needed in step 5).
- The scratchpad (plan, tool calls, observations) is persisted to disk per session so a run can be resumed or audited later — this matters in a regulated industrial setting.

### 8.2 Tool-calling format

Use the model's native tool-calling template where available (Qwen2.5, Llama-3.1/3.2, and Hermes-format fine-tunes all support structured function calling out of the box). Do **not** hand-roll a fragile "output JSON in your reply" convention if the model natively supports tool-call tokens — it is materially more reliable.

### 8.3 Required tools (v1)

| Tool | Description | Sandboxing |
|---|---|---|
| `read_file(path)` / `write_file(path, content)` | Local filesystem access, scoped to a per-session workspace directory | Path traversal blocked; workspace is chrooted/bind-mounted |
| `execute_code(language, code, timeout_s)` | Runs Python/Bash in an isolated sandbox, returns stdout/stderr/exit code | Docker container or gVisor/firejail; no network namespace; CPU/memory/time limits; disposable per call |
| `spreadsheet_op(file, operation, args)` | Read/write/formula-insert against `.xlsx`/`.csv` via a constrained API (not arbitrary code) | Runs in the same sandbox as `execute_code`; operations whitelisted (no macros) |
| `search_knowledge_base(query, filters)` | Semantic + keyword hybrid search over the local vector store (§10) | Read-only; returns chunks + source citation, never raw file paths outside the KB root |
| `ocr_document(path)` | Runs the OCR pipeline (§9.2) on an image/PDF, returns extracted text + layout | Read-only, sandboxed like code execution |
| `describe_image(path, question)` | Sends an image + question to the vision model role | Read-only |
| `build_docx(template, fields)` / `build_pptx(...)` / `build_xlsx(...)` | Calls the output-builder library (§11) | Writes only inside the session workspace |
| `list_directory(path)` | Enumerate files under a scoped root | Read-only |

Each tool has a strict JSON schema; the orchestrator validates model-emitted calls against the schema before execution and rejects/retries malformed calls rather than executing something ambiguous.

### 8.4 Guardrails specific to this environment

- **No tool may open a network socket**, ever — enforced at the sandbox level (network namespace removed), not just by convention. This is the single most important guardrail in the whole system.
- Hard **iteration cap** and **wall-clock timeout** per agent run to prevent runaway loops on a resource-constrained GPU.
- All file writes confined to a per-task workspace; nothing touches the source document store or knowledge base except through the read-only `search_knowledge_base`/`ocr_document` tools.

## 9. Multimodal Ingestion Pipeline

### 9.1 Vision-language model sizing (demo tier)

| Model family | Params | Quantized size | Fits alongside a 7B text model on 6GB? |
|---|---|---|---|
| Qwen2-VL-2B-Instruct | 2B | ~1.5–2GB (Q4) | Yes, comfortably — recommended default for the demo tier |
| Qwen2-VL-7B-Instruct | 7B | ~5GB (Q4) | Only via time-sliced swap, not co-resident |
| LLaVA-OneVision (0.5B/7B) | 0.5B / 7B | 0.5–5GB depending on variant | 0.5B variant co-resident; 7B variant swap-only |

**Recommendation for the 6GB laptop demo:** use the **small (2B-class) VLM co-resident** for quick "what's in this image" queries and time-slice-swap to the **7B VLM** only when the task explicitly needs deeper drawing/tag reading (routed via the `drawing_reading` capability tag in §7.2). This gives snappy default behavior without sacrificing accuracy on the hero demo (P&ID reading).

### 9.2 OCR pipeline (on-device, CPU-friendly — keep GPU free for the LLM)

1. **Pre-process:** deskew, denoise, contrast-normalize (OpenCV). This matters a lot for real scanned/photographed reports — see the deliberately-degraded test file in §14.
2. **Text OCR:** Tesseract (fast, CPU-only, good for clean typed text) as the first pass; fall back to **PaddleOCR** (better on noisy/rotated/handwritten-adjacent text, still CPU-viable) when Tesseract's confidence score is low.
3. **Layout/table extraction:** for structured reports/forms, run a layout model (e.g., a lightweight LayoutLM-family or a rule-based table detector) to preserve table structure before handing text to the LLM — flat OCR text loses row/column relationships that matter for inspection-reading tables.
4. **Handwriting:** flag handwritten regions separately (confidence-based) and route those crops to the VLM for a best-effort transcription with an explicit "low confidence / please verify" marker — do not silently present a guessed transcription as fact for handwritten content.
5. **Output:** structured JSON (`{"page": 1, "blocks": [{"text": ..., "bbox": ..., "confidence": ..., "type": "paragraph|table|handwriting"}]}`) — this is what feeds the agent's `ocr_document` tool result, not a flat text blob, so the agent can reason about layout when useful.

### 9.3 Engineering drawings

Treat P&ID/isometric/GA drawings as a **vision task first, OCR-assist second**: the VLM reads tag numbers, line labels, and symbol layout directly from the image; a targeted OCR pass over just the title block and tag-bubble regions (detected via simple shape/contour detection — circles for instrument bubbles, rectangles for title blocks) sharpens numeric/alphanumeric accuracy where the VLM alone might misread a tag digit. Never rely on OCR alone for a drawing — symbol topology (which line connects to which valve) is a vision problem, not a text problem.

## 10. Local Knowledge Base (RAG)

- **Embedding model:** a small, CPU-or-tiny-GPU-friendly embedding model (e.g., `bge-small-en-v1.5`, ~130MB) — this must NOT compete for the 6GB VRAM budget on the demo tier; run it on CPU or as the tiny co-resident model in §9.1's leftover headroom.
- **Vector store:** embedded, file-based (e.g., Chroma or SQLite+vector-extension) — no server process to expose a port, which also simplifies the air-gap story (nothing listening that could theoretically be reached).
- **Ingestion pipeline:** watch a designated `knowledge_base/` folder (manuals, SOPs, past correspondence, drawing indices); chunk (semantic chunking, ~500–800 tokens with overlap); embed; store with metadata (source file, page, date, document type).
- **Retrieval:** hybrid (BM25 keyword + vector similarity), re-ranked, top-k (k=4–6 on the demo tier to respect the small context window).
- **Citation discipline:** every KB-grounded claim in an agent's output must carry a `[Source: filename, page]`-style citation the user can click through to the original internal document. This is both a trust requirement and an auditability requirement in a regulated setting.
- **Update path:** re-ingestion is incremental (hash-based change detection) so adding one new SOP doesn't require re-indexing the whole corpus.

## 11. Output Builders

Real deliverables, not chat text:

- **`.docx`** (approval notes, memos): template-driven using `python-docx`, with placeholder fields the agent fills (title, findings table, recommendation, signature block) — keep a small library of org-standard templates (approval note, incident report, minutes of meeting) rather than generating layout from scratch each time, for visual consistency.
- **`.pptx`** (board presentations): `python-pptx` against a company-branded template; agent fills content placeholders, generates chart data server-side (matplotlib → embedded image, or native pptx chart objects for editability).
- **`.xlsx`** (financial models, calculation summaries): `openpyxl`; formulas must be real formulas (not hardcoded computed values) so the recipient can audit and re-run them — this is demonstrated in the financial test file in §14.
- **Calculation write-ups** (engineering calcs): a structured template (inputs → governing equation → step-by-step substitution → result table → conclusion) rendered to PDF or DOCX — this mirrors how a real calc sheet is checked/approved, and is demonstrated in the calculation test file in §14.

## 12. Model Shortlist (open-weight, self-hostable)

| Role | Candidate(s) | Why |
|---|---|---|
| General reasoning / chat / document QA | Qwen2.5-7B-Instruct, Llama-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3 | Strong instruction-following at 7–8B, good GGUF quantization support, native tool-calling templates |
| Code | Qwen2.5-Coder-7B-Instruct, DeepSeek-Coder-V2-Lite | Purpose-trained on code; noticeably better at debugging/iteration than general models at the same size |
| Vision | Qwen2-VL-2B/7B-Instruct, LLaVA-OneVision | Strong document/diagram reading, active open-weight development, good quantization support |
| Embeddings | bge-small-en-v1.5, nomic-embed-text | Small, fast, good retrieval quality for the size |
| Production-tier upgrade path | Qwen2.5-72B / a 120B-class MoE (e.g., an open Mixture-of-Experts release), DeepSeek-V-family | For the full production server tier once bigger GPUs are available — the router config makes this a drop-in swap |

This list should be treated as a **starting point, not a lock-in** — re-validate against `scripts/validate_model_config.py` (§7.3) whenever a new open-weight release looks promising; that is the entire point of the pluggable router.

## 13. Air-Gap Verification (the actual proof)

This is called out separately because the problem statement is explicit that this must be *shown*, not claimed.

1. **Network namespace isolation:** the entire application stack (model servers, agent orchestrator, sandbox containers) runs inside a network namespace / VM with **no default route configured** and, for the demo, physically **no network cable/Wi-Fi connected** to the demo laptop, or a hardware/OS-level firewall with a deny-all outbound policy plus explicit loopback-only allow rules.
2. **Live network monitor during the demo:** run a lightweight always-visible packet monitor (e.g., `nethogs`, `iftop`, or a simple custom dashboard tailing `/proc/net/dev` counters) on screen throughout every demo scenario, showing zero outbound bytes on any non-loopback interface.
3. **Sandbox network denial:** the code-execution sandbox containers are started with `--network none` (Docker) or an equivalent gVisor/firejail network-namespace strip — verified by an automated test that tries to `curl` out from inside the sandbox and asserts failure.
4. **Startup self-test:** on launch, the system runs a "sovereignty check" — attempts a benign outbound DNS/HTTP call and asserts it *fails* — and refuses to serve requests if it unexpectedly succeeds (i.e., fail loud if the air-gap has been accidentally broken, rather than silently continuing).
5. **Audit log:** every tool call, model call, and file write is logged locally with a timestamp and session ID; logs never leave the box. This log is what an auditor would review after the fact, independent of the live demo.

## 14. Test Assets

Test files sized for the demo hardware tier (6GB VRAM laptop, 7B/~5GB quantized model, small context window) have been generated to exercise each capability end-to-end. All five are provided alongside this document:

| File | Format | Exercises |
|---|---|---|
| `inspection_readings.csv` | CSV, 108 rows | Tabular data understanding, anomaly/threshold-based reasoning (a small number of rows are deliberately over-threshold — "ALARM" status — to test whether the assistant correctly flags them rather than just summarizing blindly) |
| `scanned_inspection_report.pdf` | Image-based PDF (no text layer — genuinely requires OCR) | The full §9.2 OCR pipeline: deliberately includes mild rotation, sensor noise, and uneven lighting to simulate a real phone/scanner capture; also the source document for Success Criterion #2 (OCR → findings → Word approval note) |
| `piping_isometric_drawing.png` | PNG, simplified P&ID | Vision-model tag/line reading (§9.3): a surge drum with instrument tags (LT-301, PI-302), valves (LV-301, PSV-302), line numbers, and a title block — a good analogue for Success Criterion #4 |
| `pipe_stress_calculation.pdf` | Text-layer PDF, 2 pages | Engineering-math reasoning: a full ASME B31.3 wall-thickness/MAWP calculation with inputs, governing equation, six worked steps, and a result table — use this to test whether the assistant can verify/re-derive a calculation, not just transcribe it |
| `vendor_cost_financial_model.xlsx` | Excel, 3 sheets, live formulas | Financial/spreadsheet reasoning: a vendor cost comparison (3 pump vendors) with linked assumptions and real `SUM`/cross-sheet formulas — deliberately structured so the lowest-capex vendor is **not** the lowest 10-year TCO vendor, to test whether the assistant reasons through the model rather than pattern-matching to "cheapest sticker price" |

**Suggested demo sequence using these files**, mapped to §4's success criteria:

1. Upload `inspection_readings.csv` + ask "which equipment breached threshold this week and what should I flag for maintenance" → tests routing to the general-reasoning model + tabular reasoning.
2. Upload `scanned_inspection_report.pdf` + ask "read this and draft an approval note recommending action" → tests OCR pipeline, agentic multi-step (read → extract → draft), and `.docx` output (Success Criterion #2).
3. Ask the agent to "write and run a Python script that checks every CSV row against its threshold column and lists the ALARM rows" → tests routing to the code-specialist model + sandboxed execution + iteration if the first attempt has a bug (Success Criterion #3), and can be run back-to-back with step 1's task to show two different models were used (Success Criterion #1).
4. Upload `piping_isometric_drawing.png` + ask "what is line 8"-P-1043-A1A connected to, and what's the tag of the relief valve on the surge drum" → tests vision routing and drawing comprehension (Success Criterion #4).
5. Upload `pipe_stress_calculation.pdf` + ask "verify step 3 of this calculation" → tests math reasoning/verification, a good stretch test for a 7B model's numeric reliability.
6. Upload `vendor_cost_financial_model.xlsx` + ask "which vendor should we actually select and why" → tests whether the model reasons past the more visible capex numbers to the TCO/ranking sheet.
7. Throughout 1–6, keep the network monitor from §13 visible on screen (Success Criterion #5).

**Note on test-asset limits:** a genuinely handwritten note could not be reliably synthesized (rendering "fake handwriting" defeats the point of testing an OCR/handwriting pipeline) — for that specific input type, use an actual handwritten note scanned/photographed on-site during the demo rather than a synthetic file.

## 15. Repository Structure (proposed)

```
sovereign-workbench/
├── config/
│   ├── models.yaml                # §7.2
│   ├── routing_rules.yaml
│   └── sandbox_policy.yaml
├── orchestrator/
│   ├── agent_loop.py               # §8.1
│   ├── router.py                   # §7
│   ├── tool_schemas/                # §8.3 JSON schemas
│   └── session_store/               # scratchpad persistence
├── tools/
│   ├── file_io.py
│   ├── code_sandbox.py
│   ├── spreadsheet_ops.py
│   ├── kb_search.py
│   └── output_builders/
│       ├── docx_builder.py
│       ├── pptx_builder.py
│       └── xlsx_builder.py
├── ingestion/
│   ├── ocr_pipeline.py              # §9.2
│   ├── vision_router.py             # §9.1/9.3
│   └── kb_ingest.py                 # §10
├── models/                          # local weights live here, gitignored
├── knowledge_base/                  # org SOPs/manuals live here, gitignored
├── scripts/
│   ├── validate_model_config.py     # §7.3
│   ├── sovereignty_selftest.py      # §13.4
│   └── network_monitor_dashboard.py # §13.2
├── ui/                              # thin local web UI
├── test_assets/                     # §14 files
└── docs/
    └── this-file.md
```

## 16. Implementation Phases

### Phase 0 — Environment & Air-Gap Scaffolding (foundation, do first)
- [ ] Provision the demo laptop / dev box; install NVIDIA drivers, CUDA, `llama.cpp`/Ollama.
- [ ] Stand up the network isolation (§13.1) and the sovereignty self-test (§13.4) **before writing any feature code** — every later phase should be developed and tested inside this boundary from day one, not bolted on at the end.
- [ ] Stand up the live network monitor dashboard (§13.2).
- [ ] Repository scaffolding per §15.

### Phase 1 — Model Serving & Router
- [ ] Download/quantize the shortlisted models (§12) to GGUF Q4_K_M.
- [ ] Stand up `llama.cpp`/Ollama serving for each role.
- [ ] Implement `config/models.yaml` schema + loader.
- [ ] Implement rule-based router (§7.2/7.3) with logging.
- [ ] Implement `scripts/validate_model_config.py`.
- [ ] Implement LRU model swap for the demo tier's single-GPU constraint.
- [ ] **Milestone test:** send a code prompt and a summarization prompt in sequence; confirm via logs that two different models were selected and VRAM was correctly swapped.

### Phase 2 — Agent Core
- [ ] Implement the ReAct loop (§8.1) and scratchpad persistence.
- [ ] Implement tool-call schema validation and the required tool set (§8.3).
- [ ] Implement guardrails (§8.4): iteration cap, timeout, sandbox network denial.
- [ ] **Milestone test:** an intentionally-buggy code task where the agent must observe a traceback and self-correct within the retry cap.

### Phase 3 — Multimodal Ingestion
- [ ] Stand up OCR pipeline (Tesseract → PaddleOCR fallback) (§9.2).
- [ ] Integrate the small co-resident VLM + swap-in larger VLM (§9.1).
- [ ] Implement drawing-specific tag/title-block detection assist (§9.3).
- [ ] **Milestone test:** run `scanned_inspection_report.pdf` and `piping_isometric_drawing.png` (§14) through the pipeline and manually verify extraction accuracy.

### Phase 4 — Local Knowledge Base
- [ ] Stand up embedding model + vector store (§10).
- [ ] Build ingestion watcher for `knowledge_base/`.
- [ ] Implement hybrid retrieval + citation formatting.
- [ ] **Milestone test:** ingest a handful of real (or realistic dummy) SOPs; confirm retrieved answers cite the correct source document and page.

### Phase 5 — Output Builders
- [ ] Build `.docx`/`.pptx`/`.xlsx` builders with org-standard templates (§11).
- [ ] Wire output builders as agent tools.
- [ ] **Milestone test:** full run of Success Criterion #2 (scanned report → Word approval note) end-to-end.

### Phase 6 — Integration, Hardening, Demo Rehearsal
- [ ] Run all six demo scenarios in §14 back-to-back on the actual demo hardware; measure and record latency/VRAM behavior at each model swap.
- [ ] Stress the iteration cap and timeout guardrails deliberately (adversarial test: ask for something that should legitimately fail, confirm it fails safely rather than looping).
- [ ] Confirm the sovereignty self-test and live network monitor both behave correctly under every scenario above, including when the code sandbox is invoked.
- [ ] Write the short operator runbook (how to start the stack, how to add a model, how to re-ingest the knowledge base, how to read the audit log).

## 17. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| 7B model on 6GB VRAM struggles with multi-step numeric reasoning (e.g., the calculation-verification demo) | Use the code-specialist model to *compute* rather than asking the general model to do mental arithmetic — route "verify this calculation" tasks to spawn a small Python script via `execute_code` rather than trusting free-text math from a 7B model |
| Model-swap latency (3–8s) feels sluggish in a live demo | Pre-warm the two most-likely-needed models before the demo starts; show an honest "switching model…" indicator rather than hiding the delay; on Pilot/Production tier this disappears entirely since models are co-resident |
| OCR misreads on genuinely poor scans | Confidence-scored output (§9.2) with explicit low-confidence flags surfaced to the user rather than silently presented as fact; human-in-the-loop review is part of the workflow for anything that becomes a signed approval note |
| Small model hallucinates a citation or a fact not actually in the knowledge base | Enforce citation-or-refuse: the agent's system prompt and a post-generation check require every KB-grounded sentence to trace to a retrieved chunk; if it can't, the sentence is flagged or dropped, not shipped silently |
| Air-gap accidentally broken by a misconfigured library that "phones home" (telemetry in a Python package, a font-download call, etc.) | The sovereignty self-test (§13.4) and live monitor catch this at runtime regardless of *why* an egress attempt happened; additionally, audit third-party library telemetry defaults during Phase 0 dependency selection |
| New open-weight model releases weekly; team can't chase every one | The router's config-driven design (§7) is the mitigation — evaluate new candidates against `validate_model_config.py` opportunistically, but there is no requirement to chase every release; stability of the pinned model set matters more than bleeding-edge benchmark scores in a regulated deployment |

## 18. Open Questions for Stakeholders

- What is the actual target production GPU budget/hardware, so Phase 6+ (beyond this demo) can be scoped concretely against §6's Pilot/Production tiers?
- Which specific org-standard templates (approval note format, board deck branding) should the output builders (§11) start from?
- Is a small trusted user group's RBAC needed for the first real deployment, or is single-workstation/single-user sufficient for v1 (see §3 non-goals)?
- What is the actual corpus size/format for the local knowledge base (§10) at the first real site — this affects vector-store choice and re-ingestion cadence planning.
