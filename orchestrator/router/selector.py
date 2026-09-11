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

class ModelRegistry:
    def __init__(self, registry_path: str = "/home/blue/SIH/orchestrator/router/registry.yaml", ollama_host: str = "http://127.0.0.1:11434"):
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
        if manual_model_override and manual_model_override in self.models:
            model = self.models[manual_model_override]
            return RoutingDecision(
                selected_model=model.name,
                ollama_tag=model.ollama_tag,
                task_type="manual_override",
                classification_reason=f"Manually pinned to {model.name}",
                confidence=1.0,
                vram_budget_gb=model.vram_gb,
                notes="User explicit override"
            )

        # 2. Classify task
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
        
        # Pick best candidate (prefer lowest VRAM that satisfies requirements on 6GB GPU)
        selected = sorted(candidate_models, key=lambda m: m.vram_gb)[0]

        decision = RoutingDecision(
            selected_model=selected.name,
            ollama_tag=selected.ollama_tag,
            task_type=classification.task_type,
            classification_reason=classification.reason,
            confidence=classification.confidence,
            vram_budget_gb=selected.vram_gb,
            notes=f"Selected {selected.name} ({selected.ollama_tag}) satisfying capabilities {selected.capabilities}"
        )
        return decision
