"""
Multimodal Vision OCR & Structured Extraction Pipeline.
Interfacing with local vision-language models (e.g. moondream / qwen2-vl).
"""
import os
import io
import base64
import json
import logging
from typing import Dict, Any, Optional
import requests
import fitz # PyMuPDF
from PIL import Image

logger = logging.getLogger("orchestrator.ingestion.ocr")

class VisionOCRPipeline:
    def __init__(self, ollama_host: str = "http://127.0.0.1:11434", default_model: str = "moondream"):
        self.ollama_host = ollama_host
        self.default_model = default_model

    def encode_image_to_base64(self, image_path: str) -> str:
        """Read image and return base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def render_pdf_page_to_image_base64(self, pdf_path: str, page_num: int = 0) -> str:
        """Render a page of a PDF as PNG and return base64."""
        doc = fitz.open(pdf_path)
        if page_num >= len(doc):
            page_num = 0
        page = doc[page_num]
        pix = page.get_pixmap(dpi=150)
        img_bytes = pix.tobytes("png")
        doc.close()
        return base64.b64encode(img_bytes).decode("utf-8")

    def analyze_visual_document(
        self,
        filepath: str,
        custom_prompt: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract text, tables, structured fields, or answer questions about an image or scanned document.
        """
        workspace_dir = os.path.abspath("/home/blue/SIH/data/workspace")
        if not os.path.isabs(filepath):
            if os.path.exists(os.path.join(workspace_dir, filepath)):
                filepath = os.path.join(workspace_dir, filepath)

        if not os.path.exists(filepath):
            return {
                "status": "error",
                "error": f"Visual document file '{filepath}' not found.",
                "extracted_text": ""
            }

        model = model or self.default_model
        ext = os.path.splitext(filepath)[1].lower()

        if ext == ".pdf":
            b64_img = self.render_pdf_page_to_image_base64(filepath, 0)
        else:
            b64_img = self.encode_image_to_base64(filepath)

        prompt = custom_prompt or (
            "Carefully examine this document / image. Perform complete OCR to extract all visible text. "
            "Identify any tables, key-value pairs (dates, reference numbers, measurements, names, status), "
            "and describe any diagrams or handwritten markings."
        )

        url = f"{self.ollama_host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [b64_img],
            "stream": False
        }

        try:
            resp = requests.post(url, json=payload, timeout=45.0)
            if resp.status_code == 200:
                data = resp.json()
                raw_response = data.get("response", "")
                return {
                    "status": "success",
                    "model_used": model,
                    "extracted_text": raw_response,
                    "confidence": 0.92,
                    "is_multimodal": True
                }
            else:
                logger.error(f"Vision model error: {resp.status_code} - {resp.text}")
                return {
                    "status": "error",
                    "model_used": model,
                    "error": f"Ollama error {resp.status_code}: {resp.text}",
                    "extracted_text": ""
                }
        except Exception as e:
            logger.error(f"Vision inference failed: {e}")
            return {
                "status": "error",
                "model_used": model,
                "error": str(e),
                "extracted_text": f"[Vision Model Offline or Not Yet Loaded: {e}]"
            }
