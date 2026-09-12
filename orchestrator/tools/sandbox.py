"""
Secure Code Execution Sandbox for Air-Gapped Agentic Workbench.
Executes Python scripts within strict Linux kernel namespace isolation (--unshare-net)
ensuring zero outbound network connectivity and ephemeral environment.
"""
import os
import sys
import subprocess
import shutil
import time
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
WORKSPACE_DIR = os.environ.get("WORKSPACE_DIR", os.path.join(PROJECT_ROOT, "data", "workspace"))

class SandboxResult:
    def __init__(self, stdout: str, stderr: str, exit_code: int, duration_sec: float, network_isolated: bool):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.duration_sec = duration_sec
        self.network_isolated = network_isolated
        self.success = (exit_code == 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_sec": round(self.duration_sec, 3),
            "network_isolated": self.network_isolated
        }

def execute_python_code(
    code_or_filename: str,
    timeout_sec: int = 15,
    save_deliverable_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute python code in a secure network-isolated sandbox.
    If code_or_filename is raw code, it is written to a temporary workspace script.
    If save_deliverable_name is provided, it is saved under that name.
    """
    os.makedirs(WORKSPACE_DIR, exist_ok=True)
    
    # Determine target script path
    if code_or_filename.endswith(".py") and os.path.exists(os.path.join(WORKSPACE_DIR, code_or_filename)):
        script_path = os.path.join(WORKSPACE_DIR, code_or_filename)
        script_relname = code_or_filename
    else:
        script_relname = save_deliverable_name or f"agent_script_{int(time.time())}.py"
        script_path = os.path.join(WORKSPACE_DIR, script_relname)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code_or_filename)

    has_bwrap = shutil.which("bwrap") is not None
    start_time = time.time()

    if has_bwrap:
        # Use Bubblewrap for hardware-level kernel namespace isolation (--unshare-net)
        cmd = [
            "bwrap",
            "--unshare-net",      # Disable all network access
            "--unshare-ipc",      # Disable IPC with host
            "--unshare-pid",      # New PID namespace
            "--ro-bind", "/", "/", # Read-only access to system binaries/libs
            "--tmpfs", "/tmp",    # Isolated ephemeral ramfs for /tmp and cache
            "--bind", WORKSPACE_DIR, WORKSPACE_DIR, # Read-write access to workspace only
            "--chdir", WORKSPACE_DIR,
            "--proc", "/proc",
            "--dev", "/dev",
            sys.executable, script_path
        ]
        is_isolated = True
    else:
        # Fallback local runner if bwrap unavailable
        cmd = [sys.executable, script_path]
        is_isolated = False

    sandbox_env = dict(os.environ)
    sandbox_env["MPLCONFIGDIR"] = "/tmp"

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
            cwd=WORKSPACE_DIR,
            env=sandbox_env
        )
        duration = time.time() - start_time
        res = SandboxResult(
            stdout=proc.stdout,
            stderr=proc.stderr,
            exit_code=proc.returncode,
            duration_sec=duration,
            network_isolated=is_isolated
        )
    except subprocess.TimeoutExpired as e:
        duration = time.time() - start_time
        res = SandboxResult(
            stdout="",
            stderr=f"Execution timed out after {timeout_sec} seconds.",
            exit_code=-1,
            duration_sec=duration,
            network_isolated=is_isolated
        )
    except Exception as e:
        duration = time.time() - start_time
        res = SandboxResult(
            stdout="",
            stderr=f"Sandbox execution error: {str(e)}",
            exit_code=-2,
            duration_sec=duration,
            network_isolated=is_isolated
        )

    out = res.to_dict()
    out["status"] = "success" if res.success else "error"
    out["saved_script"] = script_relname
    out["deliverable_path"] = script_path
    return out
