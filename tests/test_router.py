"""
Tests for Task Classifier and Model Selector.
Verifies task classification matrices and registry-based model routing.
"""
import unittest
import os
import tempfile
import yaml
from orchestrator.router.classifier import TaskClassifier, ClassificationResult
from orchestrator.router.selector import ModelRegistry, RoutingDecision, ModelSpec


class TestTaskClassifier(unittest.TestCase):
    def setUp(self):
        self.classifier = TaskClassifier()

    def test_classify_code_generation(self):
        prompts = [
            "Write a python script to validate CSV tolerances",
            "def calculate_pressure(volume, temp): pass",
            "Write a unit test to debug the algorithm and execute the code",
            "```python\nimport math\n```"
        ]
        for p in prompts:
            result = self.classifier.classify(p)
            self.assertEqual(result.task_type, "code_gen", f"Failed on prompt: {p}")
            self.assertTrue(result.requires_code_exec, f"Expected requires_code_exec on: {p}")
            self.assertGreater(result.confidence, 0.8)

    def test_classify_spreadsheet_calculation(self):
        p1 = "Create an excel spreadsheet with sumif formulas for pump metrics"
        res1 = self.classifier.classify(p1)
        self.assertEqual(res1.task_type, "spreadsheet_calc")
        self.assertTrue(res1.requires_spreadsheet)

        p2 = "Calculate ledger balance sheet and calculate variance"
        res2 = self.classifier.classify(p2)
        self.assertEqual(res2.task_type, "spreadsheet_calc")
        self.assertTrue(res2.requires_spreadsheet)

        # Attachment based classification
        p3 = "Check these numbers"
        res3 = self.classifier.classify(p3, attachment_types=["xlsx"])
        self.assertEqual(res3.task_type, "spreadsheet_calc")
        self.assertTrue(res3.requires_spreadsheet)

    def test_classify_docgen(self):
        prompts = [
            "Draft an official approval note for boiler maintenance",
            "Create a executive summary presentation deck in pptx",
            "Save as docx and generate report memo for management"
        ]
        for p in prompts:
            result = self.classifier.classify(p)
            self.assertEqual(result.task_type, "doc_draft", f"Failed on prompt: {p}")
            self.assertTrue(result.requires_docgen)

    def test_classify_rag_search(self):
        prompts = [
            "According to SOP manual, what is the maximum permissible pressure?",
            "Search knowledge base for emergency shutdown procedure guideline",
            "Find in standard operating procedure the regulation for valve inspection"
        ]
        for p in prompts:
            result = self.classifier.classify(p)
            self.assertEqual(result.task_type, "rag_search", f"Failed on prompt: {p}")
            self.assertTrue(result.requires_rag)

    def test_classify_vision_ocr(self):
        # Prompt with image attachment
        res1 = self.classifier.classify("Extract the text from this file", attachment_types=["png"])
        self.assertEqual(res1.task_type, "vision_ocr")
        self.assertTrue(res1.requires_vision)

        # Prompt with visual keywords
        res2 = self.classifier.classify("Inspect this scanned P&ID blueprint drawing and diagram")
        self.assertEqual(res2.task_type, "vision_ocr")
        self.assertTrue(res2.requires_vision)

    def test_classify_multi_step_plan(self):
        # Scanned inspection report + approval note docx
        res1 = self.classifier.classify(
            "Extract text from this scanned inspection report and draft an approval note docx",
            attachment_types=["png"]
        )
        self.assertEqual(res1.task_type, "multi_step_plan")
        self.assertTrue(res1.requires_vision)
        self.assertTrue(res1.requires_docgen)

        # Multi-stage command
        res2 = self.classifier.classify("First write a python script, then calculate excel formulas, and finally draft report")
        self.assertEqual(res2.task_type, "multi_step_plan")
        self.assertTrue(res2.requires_code_exec)
        self.assertTrue(res2.requires_spreadsheet)
        self.assertTrue(res2.requires_docgen)

    def test_classify_general_qa(self):
        res = self.classifier.classify("Explain the principles of fluid dynamics in high-pressure valves")
        self.assertEqual(res.task_type, "general_qa")
        self.assertGreaterEqual(res.confidence, 0.7)

    def test_classify_doc_summarize(self):
        res = self.classifier.classify("Summarize the key points and extract findings from this section")
        self.assertEqual(res.task_type, "doc_summarize")


class TestModelSelector(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_registry_path = os.path.join(self.temp_dir.name, "registry.yaml")
        
        sample_registry = {
            "models": [
                {
                    "name": "reasoning-primary",
                    "ollama_tag": "qwen2.5-coder:3b",
                    "capabilities": ["general_qa", "doc_summarize", "doc_draft", "multi_step_plan", "rag_search"],
                    "vram_gb": 2.2,
                    "context_window": 32768,
                    "description": "Reasoning model"
                },
                {
                    "name": "coding-primary",
                    "ollama_tag": "qwen2.5-coder:3b",
                    "capabilities": ["code_gen", "code_review", "spreadsheet_calc"],
                    "vram_gb": 2.2,
                    "context_window": 32768,
                    "description": "Coding model"
                },
                {
                    "name": "vision-primary",
                    "ollama_tag": "moondream",
                    "capabilities": ["vision_ocr", "drawing_analysis", "image_qa"],
                    "vram_gb": 2.0,
                    "context_window": 4096,
                    "description": "Vision model"
                },
                {
                    "name": "embeddings",
                    "ollama_tag": "nomic-embed-text",
                    "capabilities": ["embedding"],
                    "vram_gb": 0.3,
                    "context_window": 8192,
                    "description": "Embedding model"
                }
            ]
        }
        with open(self.test_registry_path, "w", encoding="utf-8") as f:
            yaml.dump(sample_registry, f)

        self.registry = ModelRegistry(registry_path=self.test_registry_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_registry_loading(self):
        self.assertEqual(len(self.registry.models), 4)
        self.assertIn("reasoning-primary", self.registry.models)
        self.assertIn("coding-primary", self.registry.models)
        self.assertIn("vision-primary", self.registry.models)
        self.assertIn("embeddings", self.registry.models)

    def test_routing_coding_task(self):
        decision = self.registry.route_task("Write a python script to validate telemetry data")
        self.assertEqual(decision.selected_model, "coding-primary")
        self.assertEqual(decision.ollama_tag, "qwen2.5-coder:3b")
        self.assertEqual(decision.task_type, "code_gen")
        self.assertEqual(decision.vram_budget_gb, 2.2)

    def test_routing_doc_draft_task(self):
        decision = self.registry.route_task("Draft an official approval note docx for management")
        self.assertEqual(decision.selected_model, "reasoning-primary")
        self.assertEqual(decision.task_type, "doc_draft")

    def test_routing_vision_task(self):
        decision = self.registry.route_task("Analyze this blueprint drawing", attachment_types=["png"])
        self.assertEqual(decision.selected_model, "vision-primary")
        self.assertEqual(decision.ollama_tag, "moondream")
        self.assertEqual(decision.task_type, "vision_ocr")
        self.assertEqual(decision.vram_budget_gb, 2.0)

    def test_manual_model_override(self):
        decision = self.registry.route_task(
            prompt="Write python script",
            manual_model_override="vision-primary"
        )
        self.assertEqual(decision.selected_model, "vision-primary")
        self.assertEqual(decision.task_type, "manual_override")
        self.assertEqual(decision.confidence, 1.0)

    def test_dynamic_model_registration(self):
        new_model = self.registry.register_model(
            name="deepseek-r1-evaluator",
            ollama_tag="deepseek-r1:7b",
            capabilities=["deep_reasoning", "formal_audit"],
            vram_gb=4.5,
            context_window=65536,
            description="Deep reasoning audit model"
        )
        self.assertEqual(new_model.name, "deepseek-r1-evaluator")
        self.assertIn("deepseek-r1-evaluator", self.registry.models)

        # Reload registry from disk to verify persistence
        reloaded = ModelRegistry(registry_path=self.test_registry_path)
        self.assertIn("deepseek-r1-evaluator", reloaded.models)
        self.assertEqual(reloaded.models["deepseek-r1-evaluator"].vram_gb, 4.5)

    def test_document_upload_auto_selection(self):
        # When ANY document is uploaded in auto-select, route to reasoning-primary
        decision_csv = self.registry.route_task("Analyze these numbers", attachment_types=["csv"])
        self.assertEqual(decision_csv.selected_model, "reasoning-primary")
        self.assertEqual(decision_csv.task_type, "doc_analysis")

        decision_xlsx = self.registry.route_task("Check trade ledger", attachment_types=["xlsx"])
        self.assertEqual(decision_xlsx.selected_model, "reasoning-primary")
        self.assertEqual(decision_xlsx.task_type, "doc_analysis")

        decision_pdf = self.registry.route_task("Summarize report", attachment_types=["pdf"])
        self.assertEqual(decision_pdf.selected_model, "reasoning-primary")

    def test_manual_model_override_formatted_labels(self):
        # Override with UI label string
        decision = self.registry.route_task(
            prompt="Analyze trade file",
            attachment_types=["csv"],
            manual_model_override="● Qwen 2.5 Coder 7B (Coding)"
        )
        self.assertEqual(decision.selected_model, "coding-primary")
        self.assertEqual(decision.task_type, "manual_override")

    def test_fallback_selection(self):
        # Even if capability isn't directly in top list, selection succeeds gracefully
        decision = self.registry.route_task("Unknown ambiguous prompt with no matched keywords")
        self.assertIsNotNone(decision.selected_model)
        self.assertIsNotNone(decision.ollama_tag)


if __name__ == "__main__":
    unittest.main()
