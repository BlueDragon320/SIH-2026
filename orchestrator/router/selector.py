"""
Model Selector & Dynamic Registry Manager for Air-Gapped Workbench.
"""
from typing import List, Dict, Any, Optional
import os
import yaml
import requests
import logging
from pydantic import BaseModel
from orchestrator.router.classifier import TaskClassifier, ClassificationResult

logger = logging.getLogger("orchestrator.router")

class ModelSpec(BaseModel):
    name: str
    ollama_tag: str
    capabilities: List[str]
    vram_gb: float
    context_window: int
    description: Optional[str] = ""

class RoutingDecision(BaseModel):
    selected_model: str
    ollama_tag: str
    task_type: str
    classification_reason: str
    confidence: float
    vram_budget_gb: float
    is_fallback: bool = False
    notes: str = ""

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_REGISTRY_PATH = os.environ.get("MODEL_REGISTRY_PATH", os.path.join(PROJECT_ROOT, "orchestrator", "router", "registry.yaml"))

class ModelRegistry:
    def __init__(self, registry_path: str = DEFAULT_REGISTRY_PATH, ollama_host: str = "http://127.0.0.1:11434"):
        self.registry_path = registry_path
        self.ollama_host = ollama_host
        self.classifier = TaskClassifier()
        self.models: Dict[str, ModelSpec] = {}
        self.load_registry()

    def load_registry(self):
        """Load model registry from YAML file."""
        if not os.path.exists(self.registry_path):
            raise FileNotFoundError(f"Registry file not found at {self.registry_path}")
        
        with open(self.registry_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            
        self.models.clear()
        for item in data.get("models", []):
            spec = ModelSpec(**item)
            self.models[spec.name] = spec
        logger.info(f"Loaded {len(self.models)} models into registry: {list(self.models.keys())}")

    def save_registry(self):
        """Save current in-memory models to registry.yaml."""
        data = {"models": [model.model_dump() for model in self.models.values()]}
        with open(self.registry_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Saved {len(self.models)} models to {self.registry_path}")

    def register_model(self, name: str, ollama_tag: str, capabilities: List[str], vram_gb: float, context_window: int, description: str = "") -> ModelSpec:
        """Dynamically add or update a model in the registry without restart."""
        spec = ModelSpec(
            name=name,
            ollama_tag=ollama_tag,
            capabilities=capabilities,
            vram_gb=vram_gb,
            context_window=context_window,
            description=description
        )
        self.models[name] = spec
        self.save_registry()
        return spec

    def list_models(self) -> List[Dict[str, Any]]:
        """List all models in registry with active Ollama status."""
        active_loaded = self.get_loaded_models_in_ollama()
        installed_tags = self.get_installed_tags_in_ollama()
        
        results = []
        for m in self.models.values():
            m_dict = m.model_dump()
            m_dict["is_installed"] = any(m.ollama_tag in tag or tag.startswith(m.ollama_tag) for tag in installed_tags)
            m_dict["is_resident"] = any(m.ollama_tag in tag or tag.startswith(m.ollama_tag) for tag in active_loaded)
            results.append(m_dict)
        return results

    def get_loaded_models_in_ollama(self) -> List[str]:
        """Query Ollama /api/ps for currently resident models."""
        try:
            resp = requests.get(f"{self.ollama_host}/api/ps", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def get_installed_tags_in_ollama(self) -> List[str]:
        """Query Ollama /api/tags for installed models on disk."""
        try:
            resp = requests.get(f"{self.ollama_host}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def pull_model(self, tag: str) -> dict:
        """Pull a model from Ollama library."""
        logger.info(f"Initiating pull for model: {tag} from Ollama at {self.ollama_host}")
        try:
            resp = requests.post(
                f"{self.ollama_host}/api/pull",
                json={"name": tag, "stream": False},
                timeout=300
            )
            if resp.status_code == 200:
                logger.info(f"Successfully pulled model: {tag}")
                return resp.json()
            else:
                try:
                    err_data = resp.json()
                    err_msg = err_data.get("error", resp.text)
                except Exception:
                    err_msg = resp.text
                logger.error(f"Failed to pull model {tag} (status {resp.status_code}): {err_msg}")
                return {"error": err_msg}
        except Exception as e:
            logger.error(f"Failed to pull model {tag}: {e}")
            return {"error": str(e)}

    def list_ollama_library(self) -> list:
        """Query Ollama /api/tags for installed models with their sizes."""
        try:
            resp = requests.get(f"{self.ollama_host}/api/tags", timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("models", [])
        except Exception as e:
            logger.error(f"Failed to list Ollama library: {e}")
        return []


    def route_task(self, prompt: str, attachment_types: Optional[List[str]] = None, manual_model_override: Optional[str] = None) -> RoutingDecision:
        """Route user prompt to best registered model based on capabilities and VRAM."""
        # 1. Check manual override
        if manual_model_override and manual_model_override != "Auto":
            target_tag = manual_model_override
            selected_model_name = manual_model_override
            vram = 4.0

            # 1a. Exact match by registered model name (e.g. 'reasoning-primary', 'coding-primary')
            if manual_model_override in self.models:
                m = self.models[manual_model_override]
                selected_model_name = m.name
                target_tag = m.ollama_tag
                vram = m.vram_gb
            else:
                # 1b. Exact match by registered model's exact ollama_tag (e.g. 'llama3.1:8b', 'deepseek-r1:7b')
                exact_match = next((m for m in self.models.values() if m.ollama_tag == manual_model_override), None)
                if exact_match:
                    selected_model_name = exact_match.name
                    target_tag = exact_match.ollama_tag
                    vram = exact_match.vram_gb
                else:
                    # 1c. Normalized match (:latest or tag strip) in registered models
                    norm_match = next((m for m in self.models.values() if m.ollama_tag.removesuffix(":latest") == manual_model_override.removesuffix(":latest")), None)
                    if norm_match:
                        selected_model_name = norm_match.name
                        target_tag = norm_match.ollama_tag
                        vram = norm_match.vram_gb
                    else:
                        # 1d. Check if tag exists in Ollama library on disk
                        installed_tags = self.get_installed_tags_in_ollama()
                        if manual_model_override in installed_tags:
                            target_tag = manual_model_override
                            selected_model_name = manual_model_override
                        else:
                            norm_inst = next((t for t in installed_tags if t.removesuffix(":latest") == manual_model_override.removesuffix(":latest")), None)
                            if norm_inst:
                                target_tag = norm_inst
                                selected_model_name = norm_inst
                            else:
                                # 1e. Fallback to prefix matching ONLY if no exact match exists
                                prefix_match = next((m for m in self.models.values() if m.ollama_tag.split(":")[0] == manual_model_override.split(":")[0]), None)
                                if prefix_match:
                                    selected_model_name = prefix_match.name
                                    target_tag = prefix_match.ollama_tag
                                    vram = prefix_match.vram_gb

            return RoutingDecision(
                selected_model=selected_model_name,
                ollama_tag=target_tag,
                task_type="manual_override",
                classification_reason=f"Manually pinned to {selected_model_name} ({target_tag})",
                confidence=1.0,
                vram_budget_gb=vram,
                notes="User explicit override"
            )

        # 2. Classify task (Auto routing mode: simple text -> fast model, files -> heavy/vision model)
        classification: ClassificationResult = self.classifier.classify(prompt, attachment_types)
        
        # 3. Match capability to model
        target_capability = classification.task_type
        candidate_models = []

        for model in self.models.values():
            if target_capability in model.capabilities:
                candidate_models.append(model)

        # Fallback mappings if specific capability has no direct match
        if not candidate_models:
            if classification.requires_vision:
                candidate_models = [m for m in self.models.values() if "vision_ocr" in m.capabilities]
            elif classification.requires_code_exec or classification.requires_spreadsheet:
                candidate_models = [m for m in self.models.values() if "code_gen" in m.capabilities]
            else:
                candidate_models = [m for m in self.models.values() if "general_qa" in m.capabilities or "multi_step_plan" in m.capabilities]

        # Final default fallback
        if not candidate_models:
            candidate_models = list(self.models.values())
        
        # Pick best candidate (prefer lowest VRAM for simple tasks, appropriate capacity for files)
        selected = sorted(candidate_models, key=lambda m: m.vram_gb)[0]

        decision = RoutingDecision(
            selected_model=selected.name,
            ollama_tag=selected.ollama_tag,
            task_type=classification.task_type,
            classification_reason=classification.reason,
            confidence=classification.confidence,
            vram_budget_gb=selected.vram_gb,
            notes=f"Auto-routed to {selected.name} ({selected.ollama_tag}) satisfying capabilities {selected.capabilities}"
        )
        return decision
