"""
Document and File Ingestion Loaders.
Extracts native text from PDFs, DOCX, CSV, TXT and identifies scanned documents.
"""
import os
import mimetypes
from typing import Dict, Any, Tuple
import fitz # PyMuPDF
from docx import Document

def inspect_and_load_file(filepath: str) -> Dict[str, Any]:
    """
    Inspect a file, detect MIME type, extract native text if available,
    or mark for Vision OCR if it is a scanned PDF or image.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")

    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    file_size = os.path.getsize(filepath)

    result = {
        "filename": filename,
        "filepath": filepath,
        "extension": ext,
        "file_size": file_size,
        "is_image": False,
        "is_scanned_pdf": False,
        "is_native_doc": False,
        "extracted_text": "",
        "page_count": 1
    }

    # Image formats
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff"]:
        result["is_image"] = True
        return result

    # Plain text / Markdown / CSV / Code
    if ext in [".txt", ".md", ".csv", ".json", ".py", ".yaml", ".yml", ".log", ".sql"]:
        result["is_native_doc"] = True
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            result["extracted_text"] = f.read()
        return result

    # Word document (.docx)
    if ext == ".docx":
        result["is_native_doc"] = True
        doc = Document(filepath)
        paras = [p.text for p in doc.paragraphs if p.text.strip()]
        result["extracted_text"] = "\n\n".join(paras)
        return result

    # PDF inspection
    if ext == ".pdf":
        doc = fitz.open(filepath)
        result["page_count"] = len(doc)
        total_text = ""
        total_images = 0
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text()
            total_text += page_text + "\n"
            total_images += len(page.get_images())
            
        doc.close()

        # If PDF has very few characters but contains images, it is a scanned PDF
        if len(total_text.strip()) < 50 and total_images > 0:
            result["is_scanned_pdf"] = True
            result["extracted_text"] = ""
        else:
            result["is_native_doc"] = True
            result["extracted_text"] = total_text.strip()
            
        return result

    # Fallback raw read
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            result["extracted_text"] = f.read()
            result["is_native_doc"] = True
    except Exception:
        result["extracted_text"] = f"[Binary or unhandled format: {ext}]"

    return result
