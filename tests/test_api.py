"""
Tests for FastAPI Orchestrator Control-Plane API (orchestrator/main.py).
Verifies all REST API endpoints:
- /health
- /v1/models & /v1/models/register
- /v1/network-status
- /v1/workspace/files, /v1/workspace/upload, /v1/workspace/download
- /v1/task, /v1/task/{id}, /v1/task/{id}/approve
- /v1/tools/{tool_name}/invoke
- /v1/audit/logs
"""
import unittest
import os
import io
from fastapi.testclient import TestClient
from orchestrator.main import app, registry, memory_store, files

class TestFastAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["airgap_mode"])
        self.assertIn("timestamp", data)

    def test_get_models(self):
        resp = self.client.get("/v1/models")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("models", data)
        self.assertIn("total_registered", data)
        self.assertGreaterEqual(data["total_registered"], 4)

        model_names = [m["name"] for m in data["models"]]
        self.assertIn("reasoning-primary", model_names)
        self.assertIn("coding-primary", model_names)
        self.assertIn("vision-primary", model_names)

    def test_register_model_dynamically(self):
        new_model_payload = {
            "name": "deepseek-coder-v2-test",
            "ollama_tag": "deepseek-coder-v2:16b",
            "capabilities": ["code_gen", "deep_analysis", "test_bench"],
            "vram_gb": 8.5,
            "context_window": 65536,
            "description": "High parameter coding model for complex refactors"
        }
        resp = self.client.post("/v1/models/register", json=new_model_payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["model"]["name"], "deepseek-coder-v2-test")

        # Verify model is immediately listable without server restart
        list_resp = self.client.get("/v1/models")
        self.assertEqual(list_resp.status_code, 200)
        names = [m["name"] for m in list_resp.json()["models"]]
        self.assertIn("deepseek-coder-v2-test", names)

    def test_get_network_status(self):
        resp = self.client.get("/v1/network-status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("airgap_status", data)
        self.assertIn("external_egress_rate_bps", data)
        self.assertIn("verified_zero_egress", data)
        self.assertIn("interfaces", data)
        self.assertIn("active_connections_count", data)

    def test_workspace_files_list(self):
        # Create a test file
        files.write_workspace_file("api_sample_file.txt", "Sample workspace test content.")

        resp = self.client.get("/v1/workspace/files")
        self.assertEqual(resp.status_code, 200)
        files_data = resp.json()
        self.assertIsInstance(files_data, list)
        filenames = [f["filename"] for f in files_data]
        self.assertIn("api_sample_file.txt", filenames)

    def test_workspace_upload_and_download(self):
        test_filename = "api_upload_test.txt"
        file_bytes = b"Air-gapped upload content verification."

        # Test upload
        files_dict = {"file": (test_filename, io.BytesIO(file_bytes), "text/plain")}
        upload_resp = self.client.post("/v1/workspace/upload", files=files_dict)
        self.assertEqual(upload_resp.status_code, 200)
        u_data = upload_resp.json()
        self.assertEqual(u_data["filename"], test_filename)
        self.assertEqual(u_data["size_bytes"], len(file_bytes))

        # Test download
        download_resp = self.client.get(f"/v1/workspace/download/{test_filename}")
        self.assertEqual(download_resp.status_code, 200)
        self.assertEqual(download_resp.content, file_bytes)

        # Test download of nonexistent file
        bad_download = self.client.get("/v1/workspace/download/nonexistent_file_xyz.txt")
        self.assertEqual(bad_download.status_code, 404)

    def test_task_submission_and_lifecycle(self):
        payload = {
            "prompt": "Write a python script to validate pressure safety thresholds",
            "attachments": []
        }
        submit_resp = self.client.post("/v1/task", json=payload)
        self.assertEqual(submit_resp.status_code, 200)
        data = submit_resp.json()
        self.assertIn("task_id", data)
        self.assertEqual(data["status"], "RUNNING")
        self.assertEqual(data["routing_decision"]["selected_model"], "coding-primary")
        self.assertEqual(data["routing_decision"]["task_type"], "code_gen")

        task_id = data["task_id"]

        # Check status endpoint
        status_resp = self.client.get(f"/v1/task/{task_id}")
        self.assertEqual(status_resp.status_code, 200)
        t_data = status_resp.json()
        self.assertEqual(t_data["task_id"], task_id)
        self.assertIn(t_data["status"], ["RUNNING", "COMPLETED", "WAITING_APPROVAL"])

        # Check approval endpoint
        approve_resp = self.client.post(f"/v1/task/{task_id}/approve")
        self.assertEqual(approve_resp.status_code, 200)
        self.assertEqual(approve_resp.json()["status"], "success")

    def test_direct_tool_invoke(self):
        # Test tool invoke file_write
        write_payload = {
            "tool_args": {
                "filename": "tool_direct_write.txt",
                "content": "Direct API tool execution"
            }
        }
        res_w = self.client.post("/v1/tools/file_write/invoke", json=write_payload)
        self.assertEqual(res_w.status_code, 200)
        self.assertEqual(res_w.json()["status"], "success")

        # Test tool invoke file_read
        read_payload = {
            "tool_args": {
                "filename": "tool_direct_write.txt"
            }
        }
        res_r = self.client.post("/v1/tools/file_read/invoke", json=read_payload)
        self.assertEqual(res_r.status_code, 200)
        self.assertEqual(res_r.json()["status"], "success")
        self.assertEqual(res_r.json()["content"], "Direct API tool execution")

    def test_audit_logs_endpoint(self):
        from orchestrator.main import audit_logger
        audit_logger.log_event("AUDIT_TEST", "API_VERIFY", input_data={"test": True})
        
        resp = self.client.get("/v1/audit/logs?limit=10")
        self.assertEqual(resp.status_code, 200)
        logs = resp.json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)
        for entry in logs:
            self.assertIn("timestamp", entry)
            self.assertIn("event_type", entry)
            self.assertIn("airgap_verified", entry)


if __name__ == "__main__":
    unittest.main()
