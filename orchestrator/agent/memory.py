"""
Task Persistence & Execution Memory for Agent Loop using SQLite.
"""
import os
import sqlite3
import json
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

DB_PATH = os.path.abspath("/home/blue/SIH/data/agent_tasks.db")

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
    final_response: Optional[str] = ""
    created_at: str
    updated_at: str

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
                final_response TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save_task(self, state: TaskState):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT OR REPLACE INTO tasks (
                task_id, prompt, status, model_assigned, ollama_tag, task_type,
                plan_json, current_step, total_steps, steps_json, deliverables_json,
                final_response, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            state.final_response,
            state.created_at,
            datetime.datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()

    def get_task(self, task_id: str) -> Optional[TaskState]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

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
            final_response=row["final_response"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

    def list_all_tasks(self, limit: int = 20) -> List[TaskState]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        
        tasks = []
        for row in rows:
            tasks.append(TaskState(
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
                final_response=row["final_response"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))
        return tasks

    def delete_task(self, task_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()
        return deleted

