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
    
    print("1. Starting FastAPI Orchestrator Backend & React Web UI on http://127.0.0.1:8000 ...")
    fastapi_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "orchestrator.main:app", "--host", "127.0.0.1", "--port", "8000"]
    )

    print("2. Starting Streamlit Frontend Canvas on http://127.0.0.1:8501 ...")
    streamlit_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501", "--server.address", "127.0.0.1", "--server.headless", "true"]
    )

    def cleanup():
        print("Stopping servers...")
        try:
            fastapi_process.terminate()
            streamlit_process.terminate()
        except Exception:
            pass

    atexit.register(cleanup)

    web_url = "http://127.0.0.1:8000"
    streamlit_url = "http://127.0.0.1:8501"

    print("Waiting for servers to initialize...")
    for _ in range(30):
        try:
            resp = urllib.request.urlopen(web_url + "/health", timeout=1)
            if resp.getcode() == 200:
                print("✓ Backend & React Web UI are live!")
                break
        except Exception:
            time.sleep(0.5)

    print("Opening React Web UI (http://127.0.0.1:8000) and Streamlit Canvas (http://127.0.0.1:8501)...")
    time.sleep(1)
    webbrowser.open(web_url)
    time.sleep(0.5)
    webbrowser.open(streamlit_url)

    print("\n---------------------------------------------------------")
    print(" System is running! Keep this window open.")
    print(" Press Ctrl+C to stop all servers.")
    print("---------------------------------------------------------\n")

    try:
        while True:
            if fastapi_process.poll() is not None:
                print("FastAPI process exited.")
                break
            if streamlit_process.poll() is not None:
                print("Streamlit process exited.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Received KeyboardInterrupt, stopping...")

if __name__ == "__main__":
    launch()
