"""
Allowlisted File Tool for Air-Gapped Agentic Workbench.
Restricts all read/write operations strictly to the workspace directory.
"""
import os
import glob
from typing import List, Dict, Any

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", os.path.join(PROJECT_ROOT, "data", "workspace"))

def _resolve_safe_path(filepath: str) -> str:
    """Ensure filepath resides within WORKSPACE_DIR and prevent path traversal."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    # If a relative path is passed, join with WORKSPACE_DIR
    if not os.path.isabs(filepath):
        target = os.path.abspath(os.path.join(WORKSPACE_DIR, filepath))
    else:
        target = os.path.abspath(filepath)
    
    if not target.startswith(WORKSPACE_DIR):
        raise PermissionError(f"Access denied: path '{filepath}' is outside sandboxed workspace '{WORKSPACE_DIR}'")
    return target

def read_workspace_file(filename: str) -> str:
    """Read contents of a file in the sandboxed workspace."""
    safe_path = _resolve_safe_path(filename)
    if not os.path.exists(safe_path):
        raise FileNotFoundError(f"File '{filename}' not found in workspace.")
    with open(safe_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def write_workspace_file(filename: str, content: str) -> str:
    """Write contents to a file in the sandboxed workspace."""
    safe_path = _resolve_safe_path(filename)
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    with open(safe_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully saved {os.path.basename(safe_path)} ({len(content.encode('utf-8'))} bytes) to workspace."

def list_workspace_files() -> List[Dict[str, Any]]:
    """List all files present in the sandboxed workspace."""
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    files = []
    for root, _, filenames in os.walk(WORKSPACE_DIR):
        for fname in filenames:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, WORKSPACE_DIR)
            stat = os.stat(full_path)
            files.append({
                "filename": rel_path,
                "size_bytes": stat.st_size,
                "modified_at": stat.st_mtime,
                "absolute_path": full_path
            })
    return sorted(files, key=lambda x: x["modified_at"], reverse=True)
