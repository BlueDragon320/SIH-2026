#!/usr/bin/env python3
"""
High-Precision PDF Generator: Model Selection & Prompt Routing Architecture
Air-Gapped Agentic AI Workbench
"""
import os
import sys
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas for dynamic total page count calculation and header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        # Header (Pages >= 2)
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1B365D")) # Navy
            self.drawString(45, 792 - 32, "AIR-GAPPED AGENTIC WORKBENCH")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#4A5568")) # Slate
            self.drawRightString(612 - 45, 792 - 32, "Intelligent Model Selection & Prompt Routing Architecture")
            
            # Top Rule
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(45, 792 - 38, 612 - 45, 792 - 38)
            self.restoreState()

        # Footer on all pages
        self.saveState()
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.75)
        self.line(45, 38, 612 - 45, 38)
        
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#0D9488")) # Teal badge
        self.drawString(45, 26, "SYSTEM ARCHITECTURE: DYNAMIC MODEL ROUTER & CLASSIFIER")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 45, 26, page_str)
        self.restoreState()


def build_model_selection_pdf(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=42,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()
    
    PRIMARY = colors.HexColor("#1B365D")     # Deep Navy
    SECONDARY = colors.HexColor("#0D9488")   # Deep Teal
    ACCENT = colors.HexColor("#2563EB")      # Royal Blue
    TEXT_DARK = colors.HexColor("#1E293B")   # Slate Dark
    BG_LIGHT = colors.HexColor("#F8FAFC")    # Slate Light
    BORDER_COLOR = colors.HexColor("#CBD5E1")# Slate Border
    BOX_BG = colors.HexColor("#F1F5F9")      # Light Box
    CALLOUT_BG = colors.HexColor("#EFF6FF")  # Blue Light
    CALLOUT_BORDER = colors.HexColor("#3B82F6")

    # Custom Typography
    title_style = ParagraphStyle(
        name='DocTitle',
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=PRIMARY,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        name='DocSubtitle',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=SECONDARY,
        spaceAfter=6
    )
    sec_heading = ParagraphStyle(
        name='SecHead',
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=13.5,
        textColor=PRIMARY,
        spaceBefore=6,
        spaceAfter=2.5,
        keepWithNext=True
    )
    body = ParagraphStyle(
        name='Body',
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.8,
        textColor=TEXT_DARK,
        spaceAfter=2.5
    )
    bullet = ParagraphStyle(
        name='Bullet',
        fontName='Helvetica',
        fontSize=7.6,
        leading=10.4,
        textColor=TEXT_DARK,
        leftIndent=8,
        firstLineIndent=-5,
        spaceAfter=1.5
    )
    table_head = ParagraphStyle(
        name='THead',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.2,
        textColor=colors.white
    )
    table_cell = ParagraphStyle(
        name='TCell',
        fontName='Helvetica',
        fontSize=7.0,
        leading=9.0,
        textColor=TEXT_DARK
    )
    table_cell_bold = ParagraphStyle(
        name='TCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.0,
        leading=9.0,
        textColor=PRIMARY
    )
    mono_style = ParagraphStyle(
        name='Mono',
        fontName='Courier',
        fontSize=6.6,
        leading=8.3,
        textColor=colors.HexColor("#0F172A")
    )

    story = []

    # Title & Subtitle Banner
    story.append(Paragraph("Intelligent Model Selection Architecture", title_style))
    story.append(Paragraph("How Model Decisions are Made from Prompts | Air-Gapped Agentic AI Workbench", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=SECONDARY, spaceBefore=0, spaceAfter=5))

    # Executive Overview Callout
    overview_text = (
        "<b>Core Routing Principle:</b> In an on-premise, air-gapped system, using a single generic LLM for every task causes high latency, GPU VRAM waste, and context bottlenecks. "
        "The system uses a <b>deterministic 5-stage selection pipeline</b> that inspects prompt semantics, keywords, file attachments, and active VRAM budgets to select the optimal model in <b>&lt; 2 milliseconds</b>."
    )
    overview_table = Table(
        [[Paragraph(overview_text, body)]],
        colWidths=[522]
    )
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CALLOUT_BG),
        ('BOX', (0, 0), (-1, -1), 1, CALLOUT_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 4))

    # Section 1: The 5-Stage Selection Pipeline
    story.append(Paragraph("1. The 5-Stage Model Selection Pipeline", sec_heading))
    story.append(Paragraph(
        "Incoming prompts and tasks pass through a hierarchical priority ladder before model invocation:",
        body
    ))

    pipeline_items = [
        "<b>Stage 1 — Explicit User Override:</b> If the user manually chooses a model (e.g. <code>qwen2.5-coder:7b</code> or <code>deepseek-r1:7b</code>), the router immediately bypasses auto-classification with 100% confidence.",
        "<b>Stage 2 — Multimodal & Document Attachment Detection:</b> Non-image files (.pdf, .docx, .xlsx, .csv, .txt) auto-route to <b>Llama 3.1 8B</b> (128k context window). Image files (.png, .jpg, scanned PDFs) auto-route to <b>Moondream Vision</b> for visual inspection.",
        "<b>Stage 3 — Regex Pattern Matrix & Intent Classification:</b> For pure text prompts in Auto mode, the <code>TaskClassifier</code> runs regex pattern matching against 6 capability domains (Coding, Spreadsheet formulas, Document drafting, RAG SOPs, Mathematics, and Summarization).",
        "<b>Stage 4 — Capability Mapping against Dynamic Registry:</b> The classified intent is mapped to registered model capability profiles defined in <code>registry.yaml</code>.",
        "<b>Stage 5 — VRAM Budgeting & Hardware Optimization:</b> If multiple models match, the router selects the candidate with the <b>lowest VRAM footprint</b> to prevent GPU Out-Of-Memory (OOM) errors."
    ]
    for item in pipeline_items:
        story.append(Paragraph(f"• {item}", bullet))

    story.append(Spacer(1, 4))

    # Section 2: Prompt Pattern Matrix & Routing Decision Table
    story.append(Paragraph("2. Prompt Trigger Matrix & Assigned Models", sec_heading))
    
    matrix_data = [
        [
            Paragraph("Prompt / Attachment Triggers", table_head),
            Paragraph("Detected Intent", table_head),
            Paragraph("Assigned Model", table_head),
            Paragraph("Ctx", table_head),
            Paragraph("VRAM", table_head),
            Paragraph("Primary Role & Capability", table_head),
        ],
        [
            Paragraph("<code>python, def, script, debug, algorithm, regex, execute code</code>", table_cell),
            Paragraph("<b>Code Generation</b>", table_cell_bold),
            Paragraph("<b>Qwen 2.5 Coder 7B</b><br/>(<code>qwen2.5-coder:7b</code>)", table_cell_bold),
            Paragraph("32k", table_cell),
            Paragraph("4.7 GB", table_cell),
            Paragraph("Python code synthesis, script debugging, automated sandbox verification.", table_cell),
        ],
        [
            Paragraph("<code>excel, spreadsheet, xlsx, csv, formula, sumif, vlookup, pivot</code>", table_cell),
            Paragraph("<b>Spreadsheet / Calc</b>", table_cell_bold),
            Paragraph("<b>Qwen 2.5 Coder 7B</b><br/>(<code>qwen2.5-coder:7b</code>)", table_cell_bold),
            Paragraph("32k", table_cell),
            Paragraph("4.7 GB", table_cell),
            Paragraph("Openpyxl workbook manipulation, financial models, formula calculation.", table_cell),
        ],
        [
            Paragraph("<code>word, docx, pptx, presentation, approval note, summary, memo</code>", table_cell),
            Paragraph("<b>Document Drafting</b>", table_cell_bold),
            Paragraph("<b>Llama 3.1 8B</b><br/>(<code>llama3.1:8b</code>)", table_cell_bold),
            Paragraph("128k", table_cell),
            Paragraph("4.9 GB", table_cell),
            Paragraph("Structured deliverable generation, professional formatting, executive memos.", table_cell),
        ],
        [
            Paragraph("<code>sop, manual, guideline, policy, regulation, clause, standard</code>", table_cell),
            Paragraph("<b>RAG Policy Search</b>", table_cell_bold),
            Paragraph("<b>Llama 3.1 8B</b><br/>(<code>llama3.1:8b</code>)", table_cell_bold),
            Paragraph("128k", table_cell),
            Paragraph("4.9 GB", table_cell),
            Paragraph("Vector knowledge base retrieval, semantic grounding, strict policy adherence.", table_cell),
        ],
        [
            Paragraph("<code>solve, equation, physics, calculus, derivation, proof, math</code>", table_cell),
            Paragraph("<b>Math & Deep Reasoning</b>", table_cell_bold),
            Paragraph("<b>DeepSeek R1 7B</b><br/>(<code>deepseek-r1:7b</code>)", table_cell_bold),
            Paragraph("32k", table_cell),
            Paragraph("4.7 GB", table_cell),
            Paragraph("Step-by-step chain-of-thought derivations, engineering and physics computations.", table_cell),
        ],
        [
            Paragraph("<code>image, drawing, p&id, diagram, scan, blueprint, photo, OCR</code>", table_cell),
            Paragraph("<b>Vision & OCR</b>", table_cell_bold),
            Paragraph("<b>Moondream 1.8B</b><br/>(<code>moondream</code>)", table_cell_bold),
            Paragraph("4k", table_cell),
            Paragraph("2.0 GB", table_cell),
            Paragraph("Visual diagram OCR, scanned equipment schematic reading, visual QA.", table_cell),
        ],
        [
            Paragraph("<code>first... then... finally, step 1, step 2, multi-tool task</code>", table_cell),
            Paragraph("<b>Multi-Step Orchestration</b>", table_cell_bold),
            Paragraph("<b>Llama 3.1 8B</b><br/>(<code>llama3.1:8b</code>)", table_cell_bold),
            Paragraph("128k", table_cell),
            Paragraph("4.9 GB", table_cell),
            Paragraph("Chains vision extraction, spreadsheet analysis, and report generation.", table_cell),
        ],
    ]

    matrix_table = Table(
        matrix_data,
        colWidths=[105, 82, 95, 28, 35, 177]
    )
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3.5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 4))

    # Page Break for clean 2-page layout
    story.append(PageBreak())

    # Section 3: Visual Routing Architecture Flow
    story.append(Paragraph("3. Visual Decision Logic Flowchart", sec_heading))
    
    flowchart_text = (
        "<b>[User Prompt & Attachments Submitted]</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├──► <b>1. Manual Override Specified?</b> ──────► [YES] ──► <b>Bind Target Model Directly (100% Conf.)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ [NO (Auto Mode)]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├──► <b>2. Document Attached (.pdf/.xlsx/.docx)?</b> ─► [YES] ──► <b>Route to Llama 3.1 8B (128k Context)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ [NO]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├──► <b>3. Image Attached (.png/.jpg/scans)?</b> ──────► [YES] ──► <b>Route to Moondream Vision (1.8B)</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ [NO (Pure Text)]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├──► <b>4. Execute Pattern Matrix on Prompt Text:</b><br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <code>python / code / def / debug</code> ───────────► <b>Qwen 2.5 Coder 7B</b> (Sandbox Runner)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <code>excel / xlsx / formula / calc</code> ─────────► <b>Qwen 2.5 Coder 7B</b> (Openpyxl Calc)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <code>math / equation / physics / solve</code> ─────► <b>DeepSeek R1 7B</b> (Chain-of-Thought)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <code>sop / manual / policy / rag</code> ────────────► <b>Llama 3.1 8B</b> (RAG KB Search)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── <code>word / docx / pptx / report / memo</code> ───────► <b>Llama 3.1 8B</b> (Doc Generator)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── <code>multi-step / sequential plan</code> ─────► <b>Llama 3.1 8B</b> (Autonomous Orchestrator)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;│<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;└──► <b>5. Capability & VRAM Filter:</b> Select lowest VRAM candidate model from <code>registry.yaml</code>"
    )
    
    flow_table = Table(
        [[Paragraph(flowchart_text, mono_style)]],
        colWidths=[522]
    )
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BOX_BG),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_COLOR),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 4))

    # Section 4: Dynamic Registry & Dynamic Model Switching
    story.append(Paragraph("4. Dynamic Model Registry & Hot-Swapping", sec_heading))
    story.append(Paragraph(
        "The model selection architecture is decoupled from code via a dynamic registry (<code>registry.yaml</code>). "
        "This provides three key operational benefits:",
        body
    ))

    reg_points = [
        "<b>Zero-Downtime Hot Registration:</b> New quantized models (e.g. <code>deepseek-coder-v2:16b</code> or custom fine-tuned models) can be registered dynamically via REST API without restarting the orchestrator daemon.",
        "<b>Automatic Model Tag Normalization:</b> If a user requests a model tag without a version suffix (e.g., <code>qwen2.5-coder</code> vs <code>qwen2.5-coder:7b</code>), the selector resolves the tag against the local Ollama disk library automatically.",
        "<b>Fault-Tolerant Fallback Cascading:</b> If an assigned specialized model is unavailable or fails, the execution graph automatically cascades to the resident general reasoning model (<code>llama3.1:8b</code>) to ensure task completion."
    ]
    for p in reg_points:
        story.append(Paragraph(f"• {p}", bullet))

    story.append(Spacer(1, 4))

    # Section 5: Summary Checklist
    story.append(Paragraph("5. Summary of Model Selection Benefits", sec_heading))
    
    summary_data = [
        [
            Paragraph("Selection Metric", table_head),
            Paragraph("System Implementation", table_head),
            Paragraph("Operational Benefit in Air-Gapped Environment", table_head),
        ],
        [
            Paragraph("<b>Routing Latency</b>", table_cell_bold),
            Paragraph("&lt; 2.0 milliseconds (Regex + In-Memory Table)", table_cell),
            Paragraph("Zero token cost and zero pre-call LLM latency overhead.", table_cell),
        ],
        [
            Paragraph("<b>Context Optimization</b>", table_cell_bold),
            Paragraph("128k window for docs, 32k for code/math", table_cell),
            Paragraph("Prevents token truncation on large financial spreadsheets or PDFs.", table_cell),
        ],
        [
            Paragraph("<b>VRAM Efficiency</b>", table_cell_bold),
            Paragraph("Least-VRAM-First prioritization (2.0GB – 4.9GB)", table_cell),
            Paragraph("Enables complete agentic execution on a single workstation GPU.", table_cell),
        ],
        [
            Paragraph("<b>Security & Air-Gap</b>", table_cell_bold),
            Paragraph("100% on-device Ollama execution (localhost)", table_cell),
            Paragraph("Zero external data egress; complete compliance with air-gapped security.", table_cell),
        ],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[105, 180, 237]
    )
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), SECONDARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(summary_table)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {output_filename}")


if __name__ == "__main__":
    out_pdf = os.path.join(os.path.dirname(__file__), "MODEL_SELECTION_GUIDE.pdf")
    build_model_selection_pdf(out_pdf)
    
    # Also create MODEL_SELECTION.pdf as a copy for convenience
    alt_pdf = os.path.join(os.path.dirname(__file__), "MODEL_SELECTION.pdf")
    shutil.copyfile(out_pdf, alt_pdf)
    print(f"Created copy: {alt_pdf}")
