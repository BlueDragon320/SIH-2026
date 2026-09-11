"""
Task Classifier module for Air-Gapped Agentic Workbench.
Classifies incoming user tasks and attachments to appropriate capability tags.
"""
from typing import List, Dict, Any, Optional
import re
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    task_type: str
    confidence: float
    reason: str
    requires_vision: bool = False
    requires_code_exec: bool = False
    requires_spreadsheet: bool = False
    requires_docgen: bool = False
    requires_rag: bool = False

class TaskClassifier:
    def __init__(self):
        # Keyword & pattern matrices for high-precision, low-latency classification
        self.code_patterns = [
            r"\b(python|script|code|function|debug|algorithm|test|unit\s*test|program|regex|execute|run\s*code)\b",
            r"\b(def\s+\w+|import\s+\w+|class\s+\w+|print\(|for\s+\w+\s+in)\b",
            r"```python"
        ]
        self.spreadsheet_patterns = [
            r"\b(excel|spreadsheet|xlsx|csv|formula|sumif|vlookup|pivot|sheet|cells?|rows?|columns?)\b",
            r"\b(calculate|sum|average|variance|balance\s*sheet|ledger)\b"
        ]
        self.vision_patterns = [
            r"\b(image|picture|drawing|p&id|scanned|scan|photo|diagram|handwritten|handwriting|blueprint|ocr)\b",
            r"\b(what\s+is\s+in\s+this\s+image|read\s+this\s+scan|inspect\s+drawing)\b"
        ]
        self.docgen_patterns = [
            r"\b(word|docx|pptx|powerpoint|presentation|deck|approval\s*note|executive\s*summary|report|memo)\b",
            r"\b(generate\s+doc|draft\s+note|create\s+deck|save\s+as\s+docx)\b"
        ]
        self.rag_patterns = [
            r"\b(sop|manual|guideline|policy|regulation|standard|clause|internal\s*docs?|procedure)\b",
            r"\b(according\s+to\s+manual|search\s+knowledge\s*base|find\s+in\s+sop)\b"
        ]
        self.summarize_patterns = [
            r"\b(summarize|summary|tldr|key\s*points|extract\s*findings|condense)\b"
        ]

    def classify(self, prompt: str, attachment_types: Optional[List[str]] = None) -> ClassificationResult:
        attachment_types = attachment_types or []
        prompt_lower = prompt.lower().strip()
        
        has_image = any(t in ["image", "png", "jpg", "jpeg", "webp", "bmp", "pdf_scanned"] for t in attachment_types)
        has_spreadsheet = any(t in ["xlsx", "xls", "csv"] for t in attachment_types)
        has_doc = any(t in ["pdf", "docx", "txt", "md"] for t in attachment_types)

        # Check for image/vision trigger first if attachment is image
        if has_image or any(re.search(p, prompt_lower) for p in self.vision_patterns):
            if any(re.search(p, prompt_lower) for p in self.docgen_patterns):
                return ClassificationResult(
                    task_type="multi_step_plan",
                    confidence=0.95,
                    reason="Multi-step workflow detected: Image OCR/Extraction combined with Document Generation (.docx/.pptx)",
                    requires_vision=True,
                    requires_docgen=True
                )
            return ClassificationResult(
                task_type="vision_ocr",
                confidence=0.95,
                reason="Visual artifact or image inspection detected requiring Vision-Language Model",
                requires_vision=True
            )

        # Multi-step complex workflow detection
        seq_match = bool(re.search(r"\b(first\b.*\b(then|finally|after)|step\s*1|and\s+then|and\s+finally|and\s+save\s+as)\b", prompt_lower))
        
        has_code = any(re.search(p, prompt_lower) for p in self.code_patterns)
        has_sheet = has_spreadsheet or any(re.search(p, prompt_lower) for p in self.spreadsheet_patterns)
        has_doc = any(re.search(p, prompt_lower) for p in self.docgen_patterns)
        has_rag = any(re.search(p, prompt_lower) for p in self.rag_patterns)
        
        # Count distinct tool requirements
        tool_counts = sum([1 for flag in [has_code, has_sheet and not has_code, has_doc, has_rag] if flag])

        if seq_match or (tool_counts >= 2 and (has_doc and (has_code or has_rag or has_sheet))):
            return ClassificationResult(
                task_type="multi_step_plan",
                confidence=0.90,
                reason=f"Multi-step orchestration request involving multiple tools (code={has_code}, doc={has_doc}, sheet={has_sheet}, rag={has_rag})",
                requires_code_exec=has_code,
                requires_spreadsheet=has_sheet,
                requires_docgen=has_doc,
                requires_rag=has_rag,
                requires_vision=has_image
            )

        # Single task type checks
        if any(re.search(p, prompt_lower) for p in self.code_patterns):
            return ClassificationResult(
                task_type="code_gen",
                confidence=0.92,
                reason="Coding/Scripting request identified requiring specialized code model and sandbox execution",
                requires_code_exec=True
            )

        if has_spreadsheet or any(re.search(p, prompt_lower) for p in self.spreadsheet_patterns):
            return ClassificationResult(
                task_type="spreadsheet_calc",
                confidence=0.90,
                reason="Spreadsheet/Formula calculation task identified requiring openpyxl tool",
                requires_spreadsheet=True
            )

        if any(re.search(p, prompt_lower) for p in self.docgen_patterns):
            return ClassificationResult(
                task_type="doc_draft",
                confidence=0.88,
                reason="Formal deliverable generation (.docx/.pptx) requested",
                requires_docgen=True
            )

        if any(re.search(p, prompt_lower) for p in self.rag_patterns):
            return ClassificationResult(
                task_type="rag_search",
                confidence=0.89,
                reason="SOP/Manual lookup requested requiring local Knowledge Base RAG retrieval",
                requires_rag=True
            )

        if any(re.search(p, prompt_lower) for p in self.summarize_patterns):
            return ClassificationResult(
                task_type="doc_summarize",
                confidence=0.85,
                reason="Document summarization task detected requiring reasoning model"
            )

        return ClassificationResult(
            task_type="general_qa",
            confidence=0.80,
            reason="General inquiry/reasoning task routed to primary reasoning model"
        )
