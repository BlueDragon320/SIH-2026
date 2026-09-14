"""
Vision OCR Tool for Air-Gapped Workbench.
Re-exports VisionOCRPipeline and helper functions from ingestion.ocr_pipeline
to satisfy the spec §8 path (orchestrator/tools/vision_ocr.py).
"""
from orchestrator.ingestion.ocr_pipeline import VisionOCRPipeline

__all__ = ["VisionOCRPipeline"]
