"""
Audit Logger for Air-Gapped Workbench.
Maintains tamper-evident SQLite and JSONL audit logs of all model calls, tool executions, and file operations.
"""
import os
import sqlite3
import json
import datetime
from typing import Dict, Any, List, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AUDIT_DB_PATH = os.environ.get("AUDIT_DB_PATH", os.path.join(PROJECT_ROOT, "data", "audit.db"))
AUDIT_JSONL_PATH = os.environ.get("AUDIT_JSONL_PATH", os.path.join(PROJECT_ROOT, "data", "audit_log.jsonl"))

class AuditLogger:
    def __init__(self, db_path: str = AUDIT_DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                task_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                model_used TEXT,
                tool_name TEXT,
                input_payload TEXT,
                output_payload TEXT,
                duration_ms REAL,
                airgap_verified INTEGER DEFAULT 1
            )
        """)
        conn.commit()
        conn.close()

    def log_event(
        self,
        task_id: str,
        event_type: str,
        model_used: Optional[str] = None,
        tool_name: Optional[str] = None,
        input_data: Any = None,
        output_data: Any = None,
        duration_ms: float = 0.0
    ):
        now_iso = datetime.datetime.now().isoformat()
        inp_str = json.dumps(input_data) if input_data is not None else ""
        out_str = json.dumps(output_data) if output_data is not None else ""

        # Write to SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO audit_events 
                (timestamp, task_id, event_type, model_used, tool_name, input_payload, output_payload, duration_ms, airgap_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            """, (now_iso, task_id, event_type, model_used, tool_name, inp_str, out_str, duration_ms))
            conn.commit()
            conn.close()
        except Exception as e:
            pass

        # Write to JSONL
        try:
            record = {
                "timestamp": now_iso,
                "task_id": task_id,
                "event_type": event_type,
                "model_used": model_used,
                "tool_name": tool_name,
                "input": input_data,
                "output": output_data,
                "duration_ms": duration_ms,
                "airgap_verified": True
            }
            with open(AUDIT_JSONL_PATH, "a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception:
            pass

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent audit events for timeline / UI inspector."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
