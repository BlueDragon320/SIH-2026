"""
FastAPI Orchestrator Control-Plane Service for Air-Gapped Agentic Workbench.
Exposes REST API endpoints for frontend, model registry, task execution, and network monitor.
"""
import os
import uuid
import datetime
import asyncio
import threading
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from orchestrator.router.selector import ModelRegistry, ModelSpec, RoutingDecision
from orchestrator.agent.graph import AgentExecutor
from orchestrator.agent.memory import TaskMemoryStore, TaskState
from orchestrator.audit.logger import AuditLogger
from network_monitor.monitor import monitor_instance
from orchestrator.tools import files
from orchestrator.rag.vector_store import LocalVectorStore
from orchestrator.ingestion.loaders import inspect_and_load_file

app = FastAPI(
    title="Air-Gapped Agentic AI Workbench API",
    version="1.0.0",
    description="Control-plane orchestrator for local multi-model execution and agentic automation."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core singletons
registry = ModelRegistry()
memory_store = TaskMemoryStore()
agent_executor = AgentExecutor()
audit_logger = AuditLogger()
vector_store = LocalVectorStore()

# Model pull progress tracking
_pull_status: Dict[str, str] = {}
_pull_lock = threading.Lock()

def _bg_pull_model(tag: str):
    try:
        res = registry.pull_model(tag)
        with _pull_lock:
            if isinstance(res, dict) and "error" in res:
                _pull_status[tag] = "failed"
                audit_logger.log_event(
                    task_id="SYSTEM",
                    event_type="MODEL_PULL_FAILED",
                    model_used=tag,
                    output_data={"error": res["error"]}
                )
            else:
                _pull_status[tag] = "completed"
                audit_logger.log_event(
                    task_id="SYSTEM",
                    event_type="MODEL_PULL_COMPLETED",
                    model_used=tag,
                    output_data=res if isinstance(res, dict) else {"result": str(res)}
                )
    except Exception as e:
        with _pull_lock:
            _pull_status[tag] = "failed"
        audit_logger.log_event(
            task_id="SYSTEM",
            event_type="MODEL_PULL_FAILED",
            model_used=tag,
            output_data={"error": str(e)}
        )


# -------------------------------------------------------------
# Request / Response Schemas
# -------------------------------------------------------------
class TaskSubmitRequest(BaseModel):
    prompt: str
    attachments: Optional[List[str]] = []
    manual_model_override: Optional[str] = None
    task_id: Optional[str] = None

class TaskSubmitResponse(BaseModel):
    task_id: str
    status: str
    routing_decision: RoutingDecision
    message: str

class ModelRegisterRequest(BaseModel):
    name: str
    ollama_tag: str
    capabilities: List[str]
    vram_gb: float
    context_window: int
    description: Optional[str] = ""

class ModelPullRequest(BaseModel):
    ollama_tag: str

class ToolInvokeRequest(BaseModel):
    tool_args: Dict[str, Any]

# -------------------------------------------------------------
# API Endpoints
# -------------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "airgap_mode": True,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.post("/v1/task", response_model=TaskSubmitResponse)
async def submit_task(req: TaskSubmitRequest, background_tasks: BackgroundTasks):
    """
    Kicks off an agent task:
    1. Classifies task & auto-selects appropriate local model from registry
    2. Logs routing decision
    3. Runs agent loop
    """
    task_id = req.task_id or f"task_{uuid.uuid4().hex[:10]}"
    
    # 1. Route task
    att_types = []
    for att in req.attachments:
        ext = os.path.splitext(att)[1].lower().replace(".", "")
        att_types.append(ext)

    routing: RoutingDecision = registry.route_task(
        prompt=req.prompt,
        attachment_types=att_types,
        manual_model_override=req.manual_model_override
    )

    # 2. Log routing audit event
    audit_logger.log_event(
        task_id=task_id,
        event_type="ROUTING_DECISION",
        model_used=routing.ollama_tag,
        input_data={"prompt": req.prompt, "attachments": req.attachments},
        output_data=routing.model_dump()
    )

    # 3. Execute agent loop asynchronously in background
    def _run_agent():
        agent_executor.run_agent_loop(
            task_id=task_id,
            prompt=req.prompt,
            ollama_tag=routing.ollama_tag,
            task_type=routing.task_type,
            attachments=req.attachments,
            model_assigned=f"{routing.selected_model} / {routing.ollama_tag}"
        )

    background_tasks.add_task(_run_agent)

    return TaskSubmitResponse(
        task_id=task_id,
        status="RUNNING",
        routing_decision=routing,
        message="Task initialized and routed successfully."
    )

@app.get("/v1/task/{task_id}")
def get_task_status(task_id: str):
    """Get real-time task status, plan, step traces, and deliverables."""
    task = memory_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return task

@app.get("/v1/tasks")
def list_tasks(limit: int = 20):
    """List recent tasks."""
    return memory_store.list_all_tasks(limit=limit)

@app.delete("/v1/task/{task_id}")
def delete_task(task_id: str):
    """Delete a task and its audit record."""
    deleted = memory_store.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    audit_logger.log_event(
        task_id=task_id,
        event_type="TASK_DELETED",
        output_data={"task_id": task_id}
    )
    return {"status": "success", "message": f"Task {task_id} deleted."}

@app.post("/v1/task/{task_id}/approve")
def approve_task_step(task_id: str):
    """Human-in-the-loop resume for a checkpointed step."""
    task = memory_store.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    task.status = "RUNNING"
    memory_store.save_task(task)
    audit_logger.log_event(
        task_id=task_id,
        event_type="HUMAN_APPROVAL",
        output_data={"action": "APPROVED"}
    )
    return {"status": "success", "message": f"Task {task_id} approved to resume."}

@app.get("/v1/models")
def get_models():
    """List all registered models and active VRAM/residence status."""
    return {
        "models": registry.list_models(),
        "total_registered": len(registry.models)
    }

@app.post("/v1/models/register")
def register_model(req: ModelRegisterRequest):
    """Dynamically register a new model without redeploying or restarting."""
    spec = registry.register_model(
        name=req.name,
        ollama_tag=req.ollama_tag,
        capabilities=req.capabilities,
        vram_gb=req.vram_gb,
        context_window=req.context_window,
        description=req.description or ""
    )
    audit_logger.log_event(
        task_id="SYSTEM",
        event_type="MODEL_REGISTERED",
        model_used=req.ollama_tag,
        input_data=req.model_dump()
    )
    return {
        "status": "success",
        "message": f"Model '{req.name}' successfully registered.",
        "model": spec.model_dump()
    }

@app.post("/v1/models/pull")
def pull_model(req: ModelPullRequest, background_tasks: BackgroundTasks):
    """Trigger background download of a model from Ollama."""
    tag = req.ollama_tag
    with _pull_lock:
        _pull_status[tag] = "pulling"

    audit_logger.log_event(
        task_id="SYSTEM",
        event_type="MODEL_PULL_INITIATED",
        model_used=tag,
        input_data=req.model_dump()
    )

    background_tasks.add_task(_bg_pull_model, tag)
    return {"status": "pulling", "ollama_tag": tag}

@app.get("/v1/models/pull/{tag}/status")
def get_model_pull_status(tag: str):
    """Check status of a model pull: pulling, completed, failed, or unknown."""
    with _pull_lock:
        status = _pull_status.get(tag)
        if not status and ":" not in tag:
            status = _pull_status.get(f"{tag}:latest")
        if not status and tag.endswith(":latest"):
            status = _pull_status.get(tag[:-7])
        if not status:
            status = "unknown"
    return {"ollama_tag": tag, "status": status}

@app.get("/v1/models/ollama-library")
def get_ollama_library(detailed: bool = False):
    """Calls registry.get_installed_tags_in_ollama() and returns the raw tag list."""
    if detailed:
        return registry.list_ollama_library()
    return registry.get_installed_tags_in_ollama()


@app.post("/v1/tools/{tool_name}/invoke")
def invoke_tool_direct(tool_name: str, req: ToolInvokeRequest):
    """Direct invocation of an internal tool."""
    res = agent_executor.execute_tool(tool_name, req.tool_args, task_id="DIRECT_API")
    return res

@app.get("/v1/network-status")
def get_network_status():
    """Live egress byte counters and air-gap proof metrics."""
    return monitor_instance.sample_network_status()

@app.get("/v1/audit/logs")
def get_audit_logs(limit: int = 50):
    """Retrieve immutable audit records."""
    return audit_logger.get_recent_logs(limit=limit)

@app.get("/v1/workspace/files")
def list_workspace_files():
    """List files currently in the sandboxed workspace."""
    return files.list_workspace_files()

@app.get("/v1/workspace/download/{filename}")
def download_workspace_file(filename: str):
    """Download a generated deliverable file."""
    safe_path = files._resolve_safe_path(filename)
    if not os.path.exists(safe_path):
        raise HTTPException(status_code=404, detail="File not found in workspace.")
    return FileResponse(safe_path, filename=filename)

@app.post("/v1/workspace/upload")
async def upload_workspace_file(file: UploadFile = File(...)):
    """Upload a file to the sandboxed workspace."""
    workspace_dir = files.WORKSPACE_DIR
    os.makedirs(workspace_dir, exist_ok=True)
    target_path = os.path.join(workspace_dir, file.filename)
    with open(target_path, "wb") as f:
        f.write(await file.read())
    return {
        "filename": file.filename,
        "absolute_path": target_path,
        "size_bytes": os.path.getsize(target_path)
    }

@app.post("/v1/knowledge-base/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """Upload and ingest a document into the local RAG vector store."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    kb_dir = os.environ.get("KB_DIR", os.path.join(project_root, "data", "knowledge_base"))
    os.makedirs(kb_dir, exist_ok=True)
    target_path = os.path.join(kb_dir, file.filename)
    with open(target_path, "wb") as f:
        f.write(await file.read())

    loaded = inspect_and_load_file(target_path)
    text = loaded.get("extracted_text", "")
    if text:
        chunks = vector_store.add_document(file.filename, text, metadata={"file_size": loaded["file_size"]})
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_indexed": chunks,
            "message": f"Successfully ingested {chunks} chunks into local vector store."
        }
    return {
        "status": "warning",
        "filename": file.filename,
        "message": "No native text extracted; image OCR pending."
    }

@app.get("/v1/knowledge-base/documents")
def list_kb_documents():
    """List all documents indexed in the local knowledge base."""
    return vector_store.list_indexed_documents()

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 4

@app.post("/v1/knowledge-base/query-chunks")
def query_kb_chunks(req: RAGQueryRequest):
    """Retrieve raw chunks from local ChromaDB with similarity scores for artifact inspection."""
    results = vector_store.hybrid_search(query=req.query, top_k=req.top_k or 4)
    return {
        "query": req.query,
        "results": results,
        "total_results": len(results)
    }

@app.get("/v1/hardware-status")
def get_hardware_status():
    """Live GPU VRAM, utilization, temperature, CPU, and RAM telemetry."""
    import subprocess
    import shutil
    import psutil

    gpu_info = {
        "available": False,
        "name": "N/A",
        "vram_total_mb": 0.0,
        "vram_used_mb": 0.0,
        "vram_free_mb": 0.0,
        "gpu_util_percent": 0.0,
        "temperature_c": 0.0
    }

    if shutil.which("nvidia-smi"):
        try:
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=1.5
            )
            if res.returncode == 0 and res.stdout.strip():
                parts = [p.strip() for p in res.stdout.strip().split(",")]
                if len(parts) >= 6:
                    gpu_info = {
                        "available": True,
                        "name": parts[0],
                        "vram_total_mb": float(parts[1]),
                        "vram_used_mb": float(parts[2]),
                        "vram_free_mb": float(parts[3]),
                        "gpu_util_percent": float(parts[4]),
                        "temperature_c": float(parts[5])
                    }
        except Exception:
            pass

    # Host CPU & RAM
    cpu_percent = 0.0
    ram_info = {"total_mb": 0.0, "used_mb": 0.0, "percent": 0.0}
    try:
        cpu_percent = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        ram_info = {
            "total_mb": round(vm.total / (1024 * 1024), 1),
            "used_mb": round(vm.used / (1024 * 1024), 1),
            "percent": vm.percent
        }
    except Exception:
        pass

    loaded_models = registry.get_loaded_models_in_ollama()

    return {
        "gpu": gpu_info,
        "cpu_percent": cpu_percent,
        "ram": ram_info,
        "loaded_models": loaded_models,
        "timestamp": datetime.datetime.now().isoformat()
    }

