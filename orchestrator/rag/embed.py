"""
Local Embedding Client using Ollama /api/embeddings.
"""
from typing import List
import requests
import logging

logger = logging.getLogger("orchestrator.rag.embed")

class LocalEmbedder:
    def __init__(self, ollama_host: str = "http://127.0.0.1:11434", model_tag: str = "nomic-embed-text"):
        self.ollama_host = ollama_host
        self.model_tag = model_tag

    def embed_text(self, text: str) -> List[float]:
        """Generate vector embedding for a single text chunk."""
        url = f"{self.ollama_host}/api/embeddings"
        payload = {
            "model": self.model_tag,
            "prompt": text
        }
        try:
            resp = requests.post(url, json=payload, timeout=(0.5, 2.0))
            if resp.status_code == 200:
                return resp.json().get("embedding", [])
            else:
                logger.error(f"Embedding error: status {resp.status_code}, {resp.text}")
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
        
        # Safe deterministic fallback embedding if model not pulled yet
        # Uses 768-dim hash-based projection
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        return [(b / 255.0) for b in (h * 24)[:768]]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate vector embeddings for a list of text chunks."""
        return [self.embed_text(t) for t in texts]
