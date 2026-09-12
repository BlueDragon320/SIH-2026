"""
Task Persistence & Execution Memory for Agent Loop using SQLite.
"""
import os
import sqlite3
import json
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.environ.get("TASK_DB_PATH", os.path.join(PROJECT_ROOT, "data", "agent_tasks.db"))

class StepRecord(BaseModel):
    step_number: int
    phase: str # PLAN, ACT, OBSERVE, REFLECT, COMPLETE
    description: str
    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Dict[str, Any]] = None
    status: str # PENDING, RUNNING, SUCCESS, RETRY, FAILED, WAITING_APPROVAL
    timestamp: str

class TaskState(BaseModel):
    task_id: str
    prompt: str
    status: str # QUEUED, RUNNING, WAITING_APPROVAL, COMPLETED, FAILED
    model_assigned: str
    ollama_tag: str
    task_type: str
    plan: List[Any] = []
    current_step: int = 0
    total_steps: int = 0
    steps: List[StepRecord] = []
    deliverables: List[Dict[str, Any]] = []
    messages: List[Dict[str, Any]] = []
    attachments: List[str] = []
    final_response: Optional[str] = ""
    created_at: str
    updated_at: str
    user_id: Optional[str] = None

class TaskMemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                status TEXT NOT NULL,
                model_assigned TEXT,
                ollama_tag TEXT,
                task_type TEXT,
                plan_json TEXT,
                current_step INTEGER,
                total_steps INTEGER,
                steps_json TEXT,
                deliverables_json TEXT,
                messages_json TEXT,
                final_response TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        # Add messages_json column if missing from legacy table schema
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN messages_json TEXT")
        except Exception:
            pass
        conn.commit()
        try:
            cur.execute("ALTER TABLE tasks ADD COLUMN user_id TEXT")
        except Exception:
            pass
        conn.commit()
        conn.close()

    def save_task(self, state: TaskState):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO tasks (
                task_id, prompt, status, model_assigned, ollama_tag, task_type,
                plan_json, current_step, total_steps, steps_json, deliverables_json,
                messages_json, final_response, created_at, updated_at, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            state.task_id,
            state.prompt,
            state.status,
            state.model_assigned,
            state.ollama_tag,
            state.task_type,
            json.dumps(state.plan),
            state.current_step,
            state.total_steps,
            json.dumps([s.model_dump() for s in state.steps]),
            json.dumps(state.deliverables),
            json.dumps(state.messages),
            state.final_response,
            state.created_at,
            datetime.datetime.now().isoformat(),
            state.user_id
        ))
        conn.commit()
        conn.close()

    def _build_task_state(self, row: sqlite3.Row) -> TaskState:
        row_keys = row.keys()
        raw_msgs = json.loads(row["messages_json"] or "[]") if "messages_json" in row_keys and row["messages_json"] else []
        
        # Fallback to single message turn for legacy database rows
        if not raw_msgs:
            raw_msgs = []
            if row["prompt"]:
                raw_msgs.append({"role": "user", "content": row["prompt"]})
            if row["final_response"]:
                raw_msgs.append({
                    "role": "assistant",
                    "content": row["final_response"],
                    "steps": json.loads(row["steps_json"] or "[]"),
                    "deliverables": json.loads(row["deliverables_json"] or "[]"),
                    "model": row["ollama_tag"],
                    "task_type": row["task_type"]
                })

        att_list = []
        for m in raw_msgs:
            if m.get("role") == "user" and m.get("attachments"):
                att_list = m.get("attachments", [])
                break

        return TaskState(
            task_id=row["task_id"],
            prompt=row["prompt"],
            status=row["status"],
            model_assigned=row["model_assigned"],
            ollama_tag=row["ollama_tag"],
            task_type=row["task_type"],
            plan=json.loads(row["plan_json"] or "[]"),
            current_step=row["current_step"],
            total_steps=row["total_steps"],
            steps=[StepRecord(**s) for s in json.loads(row["steps_json"] or "[]")],
            deliverables=json.loads(row["deliverables_json"] or "[]"),
            messages=raw_msgs,
            attachments=att_list,
            final_response=row["final_response"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            user_id=row["user_id"] if "user_id" in row_keys else None
        )

    def get_task(self, task_id: str) -> Optional[TaskState]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return self._build_task_state(row)

    def list_all_tasks(self, limit: int = 20) -> List[TaskState]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        
        return [self._build_task_state(row) for row in rows]

    def delete_task(self, task_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()
        return deleted


    def get_tasks_by_user(self, user_id: str, limit: int = 20) -> List[TaskState]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit))
        rows = cur.fetchall()
        conn.close()
        return [self._build_task_state(row) for row in rows]

    def get_task_stats_by_user(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT user_id, 
                       COUNT(*) as task_count, 
                       MAX(created_at) as last_task_at,
                       GROUP_CONCAT(DISTINCT ollama_tag) as models_csv
                FROM tasks 
                WHERE user_id IS NOT NULL 
                GROUP BY user_id
            """)
            rows = cur.fetchall()
            stats = []
            for row in rows:
                models_csv = row["models_csv"] or ""
                models_list = [m.strip() for m in models_csv.split(",") if m.strip()]
                stats.append({
                    "user_id": row["user_id"],
                    "task_count": row["task_count"],
                    "last_task_at": row["last_task_at"],
                    "models_used": models_list
                })
        except Exception:
            stats = []
        conn.close()

        # Resolve usernames from auth DB
        try:
            auth_conn = sqlite3.connect(os.path.join(PROJECT_ROOT, "data", "auth.db"))
            auth_conn.row_factory = sqlite3.Row
            auth_cur = auth_conn.cursor()
            for s in stats:
                auth_cur.execute("SELECT username FROM users WHERE id = ?", (s["user_id"],))
                row = auth_cur.fetchone()
                s["username"] = row["username"] if row else s["user_id"]
            auth_conn.close()
        except Exception:
            for s in stats:
                if "username" not in s:
                    s["username"] = s["user_id"]

        return stats
