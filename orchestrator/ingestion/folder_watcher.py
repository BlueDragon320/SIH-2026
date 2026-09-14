"""
Knowledge Base Folder Watcher Daemon for Air-Gapped Workbench (Spec §5.6).
Continuously monitors data/knowledge_base for new or modified SOPs, manuals,
and technical documents, automatically chunking, embedding, and indexing them into ChromaDB.
"""
import os
import json
import time
import threading
import logging
from typing import Dict, Any, List, Optional

from orchestrator.rag.vector_store import LocalVectorStore
from orchestrator.ingestion.loaders import inspect_and_load_file
from orchestrator.audit.logger import AuditLogger

logger = logging.getLogger("orchestrator.ingestion.folder_watcher")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_KB_DIR = os.environ.get("KB_DIR", os.path.join(PROJECT_ROOT, "data", "knowledge_base"))
STATE_FILE_NAME = ".ingest_state.json"
VALID_EXTENSIONS = {".md", ".txt", ".pdf", ".docx", ".csv", ".json"}


class KnowledgeBaseWatcher:
    def __init__(
        self,
        watch_dir: Optional[str] = None,
        vector_store: Optional[LocalVectorStore] = None,
        audit_logger: Optional[AuditLogger] = None,
        scan_interval: int = 15
    ):
        self.watch_dir = watch_dir or DEFAULT_KB_DIR
        self.vector_store = vector_store or LocalVectorStore()
        self.audit_logger = audit_logger or AuditLogger()
        self.scan_interval = scan_interval

        self._state_file = os.path.join(self.watch_dir, STATE_FILE_NAME)
        self._state: Dict[str, Dict[str, Any]] = self._load_state()

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._last_scan_time: Optional[float] = None
        self._last_ingest_time: Optional[float] = None
        self._total_ingested_count = 0

    def _load_state(self) -> Dict[str, Dict[str, Any]]:
        """Load tracked file mtimes and chunk counts from persistent JSON state."""
        if os.path.exists(self._state_file):
            try:
                with open(self._state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read ingest state file: {e}. Starting fresh state.")
        return {}

    def _save_state(self):
        """Persist current ingestion state to disk."""
        try:
            with open(self._state_file, "w", encoding="utf-8") as f:
                json.dump(self._state, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save ingest state to {self._state_file}: {e}")

    def scan_once(self) -> Dict[str, Any]:
        """
        Perform a single scan of the watched directory.
        Detects new or modified files, chunks & embeds them, and updates state.
        """
        self._last_scan_time = time.time()
        os.makedirs(self.watch_dir, exist_ok=True)

        newly_ingested: List[Dict[str, Any]] = []
        errors: List[str] = []

        try:
            candidate_files = [
                f for f in os.listdir(self.watch_dir)
                if not f.startswith(".") and not f.startswith("~")
            ]
        except Exception as e:
            err = f"Failed to list knowledge base directory '{self.watch_dir}': {e}"
            logger.error(err)
            return {"status": "error", "error": err, "ingested": []}

        for filename in sorted(candidate_files):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in VALID_EXTENSIONS:
                continue

            filepath = os.path.join(self.watch_dir, filename)
            if not os.path.isfile(filepath):
                continue

            try:
                stat = os.stat(filepath)
                mtime = stat.st_mtime
                size = stat.st_size
            except Exception as e:
                errors.append(f"Stat error on {filename}: {e}")
                continue

            # Check if file has been ingested before and hasn't changed
            prev_info = self._state.get(filename)
            if prev_info and prev_info.get("mtime") == mtime and prev_info.get("size") == size:
                continue

            # Ingest the file
            try:
                loaded = inspect_and_load_file(filepath)
                text = loaded.get("extracted_text", "")
                if not text or not text.strip():
                    logger.info(f"Watched file '{filename}' contained no native text. Skipping chunking.")
                    continue

                # Deduce departmental tagging from filename or content
                dept = "operations" if "sop" in filename.lower() or "procurement" in filename.lower() else "general"
                chunks_indexed = self.vector_store.add_document(
                    filename=filename,
                    text=text,
                    metadata={"file_size": size, "auto_ingested": True},
                    sensitivity="internal",
                    department=dept
                )

                self._state[filename] = {
                    "mtime": mtime,
                    "size": size,
                    "chunks": chunks_indexed,
                    "department": dept,
                    "sensitivity": "internal",
                    "ingested_at": time.time()
                }
                self._save_state()

                self._last_ingest_time = time.time()
                self._total_ingested_count += 1

                self.audit_logger.log_event(
                    task_id="SYSTEM",
                    event_type="AUTO_INGEST_FILE",
                    tool_name="folder_watcher",
                    input_data={"filename": filename, "file_size": size},
                    output_data={"chunks_indexed": chunks_indexed, "department": dept}
                )

                newly_ingested.append({
                    "filename": filename,
                    "chunks": chunks_indexed,
                    "size": size,
                    "department": dept
                })
                logger.info(f"[Auto-Ingest] Successfully indexed '{filename}' ({chunks_indexed} chunks).")

            except Exception as e:
                err_msg = f"Failed to auto-ingest '{filename}': {e}"
                logger.error(err_msg)
                errors.append(err_msg)

        return {
            "status": "success",
            "scanned_files_count": len(candidate_files),
            "newly_ingested_count": len(newly_ingested),
            "newly_ingested": newly_ingested,
            "errors": errors,
            "timestamp": self._last_scan_time
        }

    def _loop(self):
        """Internal daemon loop scanning periodically until stop requested."""
        logger.info(f"KnowledgeBaseWatcher thread started. Polling every {self.scan_interval}s.")
        # Perform initial scan immediately on startup
        try:
            self.scan_once()
        except Exception as e:
            logger.error(f"Error during initial folder watcher scan: {e}")

        while not self._stop_event.is_set():
            # Wait for interval or stop event
            if self._stop_event.wait(self.scan_interval):
                break
            try:
                self.scan_once()
            except Exception as e:
                logger.error(f"Error in folder watcher scan loop: {e}")

        logger.info("KnowledgeBaseWatcher thread exiting cleanly.")

    def start(self):
        """Start the background watcher thread."""
        if self._running:
            return
        self._stop_event.clear()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="KBFolderWatcher")
        self._thread.start()

    def stop(self):
        """Stop the background watcher thread."""
        if not self._running:
            return
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._running = False

    def get_status(self) -> Dict[str, Any]:
        """Return live health and status metrics for the directory watcher."""
        return {
            "running": self._running,
            "watched_dir": self.watch_dir,
            "scan_interval_sec": self.scan_interval,
            "last_scan_timestamp": self._last_scan_time,
            "last_ingest_timestamp": self._last_ingest_time,
            "total_ingested_files": len(self._state),
            "tracked_files": list(self._state.keys())
        }


def start_watcher(
    watch_dir: Optional[str] = None,
    vector_store: Optional[LocalVectorStore] = None,
    audit_logger: Optional[AuditLogger] = None,
    scan_interval: int = 15
) -> KnowledgeBaseWatcher:
    """Convenience helper to instantiate and start a KnowledgeBaseWatcher daemon."""
    watcher = KnowledgeBaseWatcher(
        watch_dir=watch_dir,
        vector_store=vector_store,
        audit_logger=audit_logger,
        scan_interval=scan_interval
    )
    watcher.start()
    return watcher
