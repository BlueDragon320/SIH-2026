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


    def resolve_model_override(self, override: str) -> Optional[ModelSpec]:
        """Resolve a manual model override string (tag, name, or UI label) to ModelSpec."""
        if not override or override == "Auto":
            return None
        
        override_clean = override.strip()
        
        # 1. Exact match by registered model name (e.g. 'reasoning-primary')
        if override_clean in self.models:
            return self.models[override_clean]
        
        # 2. Exact match by registered model's exact ollama_tag (e.g. 'llama3.1:8b')
        for m in self.models.values():
            if m.ollama_tag == override_clean:
                return m
                
        # 3. Normalized tag match (strip :latest or add :latest)
        norm_override = override_clean.removesuffix(":latest")
        for m in self.models.values():
            if m.ollama_tag.removesuffix(":latest") == norm_override:
                return m

        # 4. Search within UI formatted labels or substrings (e.g. '● Llama 3.1 8B (General & Docs)')
        override_lower = override_clean.lower()
        if "llama" in override_lower or "3.1" in override_lower:
            llama_m = self.models.get("reasoning-primary") or next((m for m in self.models.values() if "llama" in m.ollama_tag.lower()), None)
            if llama_m:
                return llama_m
        if "qwen" in override_lower or "coder" in override_lower:
            qwen_m = self.models.get("coding-primary") or next((m for m in self.models.values() if "qwen" in m.ollama_tag.lower()), None)
            if qwen_m:
                return qwen_m
        if "deepseek" in override_lower or "r1" in override_lower:
            ds_m = self.models.get("math-engineering") or next((m for m in self.models.values() if "deepseek" in m.ollama_tag.lower()), None)
            if ds_m:
                return ds_m
        if "moondream" in override_lower or "vision" in override_lower:
            moon_m = self.models.get("vision-primary") or next((m for m in self.models.values() if "moondream" in m.ollama_tag.lower()), None)
            if moon_m:
                return moon_m

        # 5. Check if any registered model's tag or name appears in override string
        for m in self.models.values():
            if m.ollama_tag.lower() in override_lower or m.name.lower() in override_lower:
                return m

        # 6. Check installed tags in Ollama library on disk
        installed_tags = self.get_installed_tags_in_ollama()
        for t in installed_tags:
            if t == override_clean or t.removesuffix(":latest") == norm_override or t.lower() in override_lower:
                return ModelSpec(
                    name=t,
                    ollama_tag=t,
                    capabilities=["general_qa"],
                    vram_gb=4.5,
                    context_window=32768,
                    description=f"Installed Ollama model: {t}"
                )

        return None

    def route_task(self, prompt: str, attachment_types: Optional[List[str]] = None, manual_model_override: Optional[str] = None) -> RoutingDecision:
        """Route user prompt to best registered model based on capabilities and VRAM."""
        # 1. Check manual override (highest priority)
        if manual_model_override and manual_model_override != "Auto":
            spec = self.resolve_model_override(manual_model_override)
            if spec:
                return RoutingDecision(
                    selected_model=spec.name,
                    ollama_tag=spec.ollama_tag,
                    task_type="manual_override",
                    classification_reason=f"Manually pinned to {spec.name} ({spec.ollama_tag})",
                    confidence=1.0,
                    vram_budget_gb=spec.vram_gb,
                    notes="User explicit override"
                )
            else:
                return RoutingDecision(
                    selected_model=manual_model_override,
                    ollama_tag=manual_model_override,
                    task_type="manual_override",
                    classification_reason=f"Manually pinned to {manual_model_override}",
                    confidence=1.0,
                    vram_budget_gb=4.5,
                    notes="User explicit override"
                )

        # 2. Check if non-image documents are uploaded (CSV, XLSX, XLS, PDF, DOCX, TXT, JSON, etc.)
        # When in Auto-Select mode, ANY document upload MUST automatically route to reasoning-primary (Llama 3.1 8B, 128k context)
        non_image_docs = [
            t for t in (attachment_types or [])
            if t.lower() not in ["image", "png", "jpg", "jpeg", "webp", "bmp"]
        ]
        if non_image_docs:
            llama_model = self.models.get("reasoning-primary") or next((m for m in self.models.values() if "llama3.1" in m.ollama_tag), None)
            if llama_model:
                return RoutingDecision(
                    selected_model=llama_model.name,
                    ollama_tag=llama_model.ollama_tag,
                    task_type="doc_analysis",
                    classification_reason=f"Document upload ({', '.join(non_image_docs)}) detected - auto-selected Llama 3.1 8B (128k context)",
                    confidence=0.98,
                    vram_budget_gb=llama_model.vram_gb,
                    notes=f"Auto-routed document upload to {llama_model.name} ({llama_model.ollama_tag})"
                )

        # 3. Classify task (Auto routing mode without document uploads)
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
