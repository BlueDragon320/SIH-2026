import subprocess
import time
import urllib.request
import webbrowser
import atexit
import sys
import os

def launch():
    print("=========================================================")
    print("   Air-Gapped Agentic AI Workbench Launcher")
    print("=========================================================")
    
    project_dir = os.path.abspath(os.path.dirname(__file__))
    frontend_web_dir = os.path.join(project_dir, "frontend-web")

    print("1. Starting FastAPI Orchestrator Backend on http://127.0.0.1:8000 ...")
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "orchestrator.main:app", "--host", "127.0.0.1", "--port", "8000"]
    )

    print("2. Starting React Web UI (Vite) on http://127.0.0.1:5173 ...")
    # Launch Vite via npm run dev in frontend-web
    cmd = ["npm.cmd" if os.name == "nt" else "npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "5173"]
    react_process = subprocess.Popen(
        cmd,
        cwd=frontend_web_dir
    )

    def cleanup():
        print("Stopping servers...")
        try:
            fastapi_process.terminate()
            react_process.terminate()
        except Exception:
            pass

    atexit.register(cleanup)

    web_url = "http://127.0.0.1:8000"
    react_url = "http://127.0.0.1:5173"

    print("Waiting for servers to initialize...")
    for _ in range(30):
        try:
            resp = urllib.request.urlopen(web_url + "/health", timeout=1)
            if resp.getcode() == 200:
                print("✓ Backend is live!")
                break
        except Exception:
            time.sleep(0.5)

    print("Opening React Web UI (http://127.0.0.1:5173)...")
    time.sleep(1.5)
    webbrowser.open(react_url)

    print("\n---------------------------------------------------------")
    print(" System is running!")
    print(" React Web UI:     http://127.0.0.1:5173")
    print(" Orchestrator API: http://127.0.0.1:8000")
    print(" Press Ctrl+C to stop all servers.")
    print("---------------------------------------------------------\n")

    try:
        while True:
            if fastapi_process.poll() is not None:
                print("FastAPI process exited.")
                break
            if react_process.poll() is not None:
                print("React Web UI process exited.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, stopping...")

if __name__ == "__main__":
    launch()
