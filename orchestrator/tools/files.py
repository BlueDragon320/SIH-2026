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
    """Read contents of a file in the sandboxed workspace with structured format extraction."""
    safe_path = _resolve_safe_path(filename)
    if not os.path.exists(safe_path):
        raise FileNotFoundError(f"File '{filename}' not found in workspace.")
    
    ext = os.path.splitext(filename)[1].lower()

    # 1. Excel Spreadsheets (.xlsx, .xls)
    if ext in [".xlsx", ".xls"]:
        try:
            import pandas as pd
            xl = pd.ExcelFile(safe_path)
            sheets_content = []
            for sheet in xl.sheet_names:
                df = xl.parse(sheet).dropna(how="all")
                sheets_content.append(f"### Sheet: {sheet}\n" + df.to_string(index=False))
            return "\n\n".join(sheets_content)
        except Exception as e:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(safe_path, data_only=True)
                sheets_content = []
                for sheet in wb.sheetnames:
                    ws = wb[sheet]
                    rows = []
                    for row in ws.iter_rows(values_only=True):
                        if any(c is not None for c in row):
                            rows.append(" | ".join([str(c) if c is not None else "" for c in row]))
                    sheets_content.append(f"### Sheet: {sheet}\n" + "\n".join(rows))
                return "\n\n".join(sheets_content)
            except Exception as e2:
                return f"[Excel Extraction Error: {e} / {e2}]"

    # 2. Word Documents (.docx)
    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(safe_path)
            lines = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    lines.append(" | ".join([c.text.strip() for c in row.cells]))
            return "\n".join(lines)
        except Exception as e:
            return f"[Docx Extraction Error: {e}]"

    # 3. PDF Documents (.pdf)
    if ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(safe_path)
            pages = [page.get_text() for page in doc]
            return "\n\n".join(pages)
        except Exception as e:
            return f"[PDF Extraction Error: {e}]"

    # 4. Standard Text / CSV / JSON / Scripts
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
