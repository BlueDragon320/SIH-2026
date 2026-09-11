"""
Tests for Secure Code Execution Sandbox (orchestrator/tools/sandbox.py).
Verifies isolated Python execution, deliverable artifact generation,
timeout bounds, and hard Linux namespace network isolation (--unshare-net).
"""
import unittest
import os
import time
from orchestrator.tools import sandbox, files


class TestCodeExecutionSandbox(unittest.TestCase):
    def setUp(self):
        self.workspace = files.WORKSPACE_DIR
        os.makedirs(self.workspace, exist_ok=True)
        self.created_scripts = []

    def tearDown(self):
        for s in self.created_scripts:
            p = os.path.join(self.workspace, s)
            if os.path.exists(p):
                os.remove(p)

    def test_successful_python_execution(self):
        code = """
import math
vals = [10.5, 20.2, 30.8, 40.1]
mean = sum(vals) / len(vals)
std = math.sqrt(sum((x - mean) ** 2 for x in vals) / len(vals))
print(f"MEAN={mean:.2f}, STD={std:.2f}")
"""
        res = sandbox.execute_python_code(code)
        if res.get("saved_script"):
            self.created_scripts.append(res["saved_script"])

        self.assertTrue(res["success"])
        self.assertEqual(res["exit_code"], 0)
        self.assertIn("MEAN=25.40, STD=11.12", res["stdout"])
        self.assertEqual(res["stderr"], "")
        self.assertTrue(res["network_isolated"])
        self.assertGreater(res["duration_sec"], 0.0)

    def test_script_deliverable_saved(self):
        script_name = "tolerance_validator.py"
        self.created_scripts.append(script_name)

        code = """
def check_tolerance(val, target, tol):
    return abs(val - target) <= tol

print("CHECK_PASS:", check_tolerance(100.2, 100.0, 0.5))
"""
        res = sandbox.execute_python_code(code, save_deliverable_name=script_name)

        self.assertTrue(res["success"])
        self.assertEqual(res["saved_script"], script_name)
        self.assertTrue(os.path.exists(res["deliverable_path"]))
        self.assertIn("CHECK_PASS: True", res["stdout"])

        # Check saved file content
        with open(res["deliverable_path"], "r", encoding="utf-8") as f:
            saved_content = f.read()
        self.assertIn("def check_tolerance", saved_content)

    def test_execute_existing_workspace_script(self):
        script_name = "pre_existing_script.py"
        self.created_scripts.append(script_name)
        script_path = os.path.join(self.workspace, script_name)

        with open(script_path, "w", encoding="utf-8") as f:
            f.write("print('EXECUTING PRE-EXISTING SCRIPT')\n")

        res = sandbox.execute_python_code(script_name)
        self.assertTrue(res["success"])
        self.assertIn("EXECUTING PRE-EXISTING SCRIPT", res["stdout"])

    def test_runtime_error_handling(self):
        code = """
def divide_pressure(p, v):
    return p / v

divide_pressure(100, 0)
"""
        res = sandbox.execute_python_code(code)
        if res.get("saved_script"):
            self.created_scripts.append(res["saved_script"])

        self.assertFalse(res["success"])
        self.assertNotEqual(res["exit_code"], 0)
        self.assertIn("ZeroDivisionError: division by zero", res["stderr"])

    def test_timeout_enforcement(self):
        code = """
import time
time.sleep(5)
print("Should not reach here")
"""
        res = sandbox.execute_python_code(code, timeout_sec=1)
        if res.get("saved_script"):
            self.created_scripts.append(res["saved_script"])

        self.assertFalse(res["success"])
        self.assertEqual(res["exit_code"], -1)
        self.assertIn("timed out after 1 seconds", res["stderr"])

    def test_network_isolation_socket_unreachable(self):
        """
        Air-Gap Proof: Verify that attempting an external TCP connection fails
        with [Errno 101] Network is unreachable due to --unshare-net namespace isolation.
        """
        code = """
import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2.0)
try:
    s.connect(('8.8.8.8', 53))
    print("LEAK: Connected to external host!")
    sys.exit(0)
except Exception as e:
    print(f"ISOLATION_VERIFIED: {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(1)
"""
        res = sandbox.execute_python_code(code)
        if res.get("saved_script"):
            self.created_scripts.append(res["saved_script"])

        self.assertFalse(res["success"])
        self.assertNotEqual(res["exit_code"], 0)
        self.assertIn("ISOLATION_VERIFIED", res["stderr"])
        self.assertTrue(
            "Network is unreachable" in res["stderr"] or "OSError" in res["stderr"] or "socket" in res["stderr"].lower(),
            f"Expected network unreachable error, got: {res['stderr']}"
        )
        self.assertTrue(res["network_isolated"])

    def test_network_isolation_dns_failure(self):
        """
        Air-Gap Proof: Verify that DNS resolution attempts fail in the sandbox.
        """
        code = """
import socket
import sys

try:
    ip = socket.gethostbyname('example.com')
    print(f"LEAK: Resolved DNS {ip}")
    sys.exit(0)
except Exception as e:
    print(f"DNS_BLOCKED: {type(e).__name__}: {e}", file=sys.stderr)
    sys.exit(1)
"""
        res = sandbox.execute_python_code(code)
        if res.get("saved_script"):
            self.created_scripts.append(res["saved_script"])

        self.assertFalse(res["success"])
        self.assertNotEqual(res["exit_code"], 0)
        self.assertIn("DNS_BLOCKED", res["stderr"])


if __name__ == "__main__":
    unittest.main()
