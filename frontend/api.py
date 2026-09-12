"""
API Client & Telemetry Helpers for Air-Gapped Workbench UI.
"""
import os
import requests
import subprocess
import pandas as pd

API_BASE_URL = os.environ.get("WORKBENCH_API_URL", "http://127.0.0.1:8000")

def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=4.0)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_post(endpoint: str, data: dict = None, files: dict = None):
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}", json=data, files=files, timeout=60.0)
        return r.json() if r.status_code in [200, 201] else {"error": r.text, "status_code": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def api_delete(endpoint: str):
    try:
        r = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=5.0)
        return r.json() if r.status_code in [200, 204] else None
    except Exception:
        return None

def get_gpu_telemetry():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            text=True, timeout=1.0
        ).strip().split(",")
        if len(out) >= 4:
            name = out[0].strip()
            short_name = name.replace("NVIDIA ", "").replace("GeForce ", "").replace(" Laptop GPU", "").replace(" GPU", "")
            util = out[1].strip()
            mem_used = int(out[2].strip())
            mem_total = int(out[3].strip())
            return {
                "name": name,
                "short_name": short_name,
                "util": f"{util}%",
                "mem": f"{round(mem_used/1024, 1)}/{round(mem_total/1024, 1)}GB"
            }
    except Exception:
        pass
    return {"name": "RTX 5050", "short_name": "RTX 5050", "util": "0%", "mem": "0.0/8.0GB"}

def get_file_mime(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mimes = {
        ".py": "text/x-python",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".pdf": "application/pdf",
        ".sh": "text/x-sh",
    }
    return mimes.get(ext, "application/octet-stream")
