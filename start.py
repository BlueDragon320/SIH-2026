#!/usr/bin/env python3
"""
Air-Gapped Agentic AI Workbench - Unified Cross-Platform Executable Launcher
Works seamlessly on Linux, Windows, and macOS.
1. Checks & launches Ollama runtime (11434)
2. Checks & launches FastAPI Orchestrator (8000)
3. Checks & launches Modern React Web UI (5173)
4. Automatically redirects & opens browser to http://localhost:5173
"""

import os
import sys
import time
import shutil
import urllib.request
import subprocess
import webbrowser
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend-web"
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def is_endpoint_up(url: str, timeout: float = 1.0) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WorkbenchLauncher/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status in (200, 204, 301, 302, 404)
    except Exception:
        return False

def get_python_exe() -> str:
    venv_py = ROOT_DIR / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if venv_py.exists() and os.access(venv_py, os.X_OK if os.name != "nt" else os.F_OK):
        return str(venv_py)
    alt_venv = ROOT_DIR / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if alt_venv.exists():
        return str(alt_venv)
    return sys.executable

def main():
    print("=" * 68)
    print("🛡️  Air-Gapped Agentic AI Workbench - Launching Services...")
    print("=" * 68)

    py_exe = get_python_exe()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR) + (os.pathsep + env.get("PYTHONPATH", "") if env.get("PYTHONPATH") else "")
    env["OLLAMA_HOST"] = "127.0.0.1:11434"
    env["OLLAMA_MAX_LOADED_MODELS"] = "2"
    env["OLLAMA_NUM_PARALLEL"] = "1"
    env["OLLAMA_KEEP_ALIVE"] = "15m"

    # Local models folder detection
    for cand in [ROOT_DIR / "models", ROOT_DIR / "Models"]:
        if (cand / "blobs").exists():
            env["OLLAMA_MODELS"] = str(cand)
            break

    # 1. Ollama Daemon
    if not is_endpoint_up("http://127.0.0.1:11434/api/tags"):
        print("[1/3] Starting background Ollama daemon (Port 11434)...")
        ollama_bin = shutil.which("ollama")
        if not ollama_bin and os.name == "nt":
            appdata_ollama = Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"
            if appdata_ollama.exists():
                ollama_bin = str(appdata_ollama)

        if ollama_bin:
            ollama_log = open(DATA_DIR / "ollama_runtime.log", "a")
            subprocess.Popen([ollama_bin, "serve"], env=env, stdout=ollama_log, stderr=ollama_log, start_new_session=True)
            for _ in range(15):
                if is_endpoint_up("http://127.0.0.1:11434/api/tags"):
                    break
                time.sleep(1)
        else:
            print("      ⚠️ Ollama binary not found in PATH. Proceeding...")
    else:
        print("[1/3] ✓ Ollama daemon is already running (Port 11434)")

    # 2. FastAPI Orchestrator
    if not is_endpoint_up("http://127.0.0.1:8000/health"):
        print("[2/3] Starting FastAPI Control-Plane Orchestrator (Port 8000)...")
        orch_log = open(DATA_DIR / "orchestrator.log", "a")
        uvicorn_cmd = [py_exe, "-m", "uvicorn", "orchestrator.main:app", "--host", "127.0.0.1", "--port", "8000"]
        subprocess.Popen(uvicorn_cmd, cwd=str(ROOT_DIR), env=env, stdout=orch_log, stderr=orch_log, start_new_session=True)
        for _ in range(15):
            if is_endpoint_up("http://127.0.0.1:8000/health"):
                break
            time.sleep(1)
        print("      ✓ FastAPI Orchestrator active on http://127.0.0.1:8000")
    else:
        print("[2/3] ✓ FastAPI Orchestrator is already running (Port 8000)")

    # 3. Modern React Web UI (Vite)
    if not is_endpoint_up("http://127.0.0.1:5173"):
        print("[3/3] Starting Modern React Web UI on port 5173 (0.0.0.0)...")
        ui_log = open(DATA_DIR / "frontend_web.log", "a")
        npm_bin = shutil.which("npm") or ("npm.cmd" if os.name == "nt" else None)
        if npm_bin:
            cmd = [npm_bin, "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
        else:
            cmd = ["node", "./node_modules/.bin/vite", "--host", "0.0.0.0", "--port", "5173"]
        subprocess.Popen(cmd, cwd=str(FRONTEND_DIR), env=env, stdout=ui_log, stderr=ui_log, start_new_session=True)
        for _ in range(15):
            if is_endpoint_up("http://127.0.0.1:5173"):
                break
            time.sleep(1)
        print("      ✓ Modern React Web UI active on http://localhost:5173")
    else:
        print("[3/3] ✓ Modern React Web UI is already running (Port 5173)")

    print("=" * 68)
    print("✅ All Air-Gapped Workbench services are online!")
    print("   • Web Dashboard:     http://localhost:5173")
    print("   • Backend API Docs:  http://127.0.0.1:8000/docs")
    print("   • Ollama Runtime:    http://127.0.0.1:11434")
    print("=" * 68)

    # 4. Auto-redirect / launch default web browser
    target_url = "http://localhost:5173"
    print(f"\n🚀 Redirecting to frontend: Opening {target_url} in default browser...")
    try:
        webbrowser.open(target_url, new=2, autoraise=True)
    except Exception as e:
        print(f"Browser launch note: {e}")

if __name__ == "__main__":
    main()
