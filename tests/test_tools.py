"""
Tests for Secure Tool Layer:
- files.py: Path-allowlisted sandbox workspace file operations & traversal protection
- spreadsheet.py: Audit-ready Excel calculation engine with live formula generation
- docgen.py: Official .docx approval note & .pptx executive deck generation
"""
import unittest
import os
import shutil
from docx import Document
from pptx import Presentation
import openpyxl

from orchestrator.tools import files, spreadsheet, docgen

class TestFilesTool(unittest.TestCase):
    def setUp(self):
        self.workspace = files.WORKSPACE_DIR
        os.makedirs(self.workspace, exist_ok=True)
        self.test_files = []

    def tearDown(self):
        for fname in self.test_files:
            p = os.path.join(self.workspace, fname)
            if os.path.exists(p):
                os.remove(p)

    def test_write_and_read_workspace_file(self):
        filename = "test_note.txt"
        self.test_files.append(filename)
        content = "Air-Gapped Autonomous Agent Report - Test Sample Content."

        write_res = files.write_workspace_file(filename, content)
        self.assertIn("Successfully saved", write_res)
        self.assertTrue(os.path.exists(os.path.join(self.workspace, filename)))

        read_content = files.read_workspace_file(filename)
        self.assertEqual(read_content, content)

    def test_list_workspace_files(self):
        f1 = "file_a.txt"
        f2 = "file_b.json"
        self.test_files.extend([f1, f2])

        files.write_workspace_file(f1, "Data A")
        files.write_workspace_file(f2, '{"key": "value"}')

        file_list = files.list_workspace_files()
        filenames = [f["filename"] for f in file_list]
        self.assertIn(f1, filenames)
        self.assertIn(f2, filenames)

        for item in file_list:
            self.assertIn("filename", item)
            self.assertIn("size_bytes", item)
            self.assertIn("modified_at", item)
            self.assertIn("absolute_path", item)

    def test_path_traversal_protection(self):
        malicious_paths = [
            "../../etc/passwd",
            "../../../secret.env",
            "/etc/shadow",
            "/tmp/outside_workspace.txt",
            "subdir/../../../../root/.bashrc"
        ]
        for bad_path in malicious_paths:
            with self.assertRaises(PermissionError, msg=f"Should reject: {bad_path}"):
                files.write_workspace_file(bad_path, "Malicious write attempt")

            with self.assertRaises(PermissionError, msg=f"Should reject: {bad_path}"):
                files.read_workspace_file(bad_path)

    def test_read_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            files.read_workspace_file("nonexistent_ghost_file_12345.txt")


class TestSpreadsheetTool(unittest.TestCase):
    def setUp(self):
        self.test_files = []

    def tearDown(self):
        for fname in self.test_files:
            p = os.path.join(files.WORKSPACE_DIR, fname)
            if os.path.exists(p):
                os.remove(p)

    def test_create_and_read_audit_spreadsheet(self):
        filename = "pump_inspection_telemetry.xlsx"
        self.test_files.append(filename)

        headers = ["Pump ID", "Vibration (mm/s)", "Pressure (bar)", "Temp (C)", "Status"]
        rows = [
            ["P-101", 1.2, 45.0, 68.5, "NORMAL"],
            ["P-102", 3.8, 48.2, 82.0, "WARNING"],
            ["P-103", 0.9, 44.5, 65.0, "NORMAL"],
            ["P-104", 4.5, 52.1, 91.2, "CRITICAL"]
        ]
        summary_formulas = {
            "Average Vibration": "=AVERAGE(B2:B5)",
            "Max Temperature": "=MAX(D2:D5)"
        }

        res = spreadsheet.create_audit_spreadsheet(
            filename=filename,
            sheet_title="PumpTelemetry",
            headers=headers,
            rows=rows,
            summary_formulas=summary_formulas,
            title="CRITICAL EQUIPMENT TELEMETRY AUDIT"
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["rows_count"], 4)
        self.assertEqual(res["columns_count"], 5)
        self.assertTrue(os.path.exists(res["absolute_path"]))

        # Read back using tool
        read_res = spreadsheet.read_spreadsheet(filename)
        self.assertEqual(read_res["filename"], filename)
        self.assertIn("PumpTelemetry", read_res["sheets"])
        sheet_rows = read_res["sheets"]["PumpTelemetry"]
        self.assertGreater(len(sheet_rows), 5)

        # Direct openpyxl verification of formulas
        wb = openpyxl.load_workbook(res["absolute_path"], data_only=False)
        ws = wb["PumpTelemetry"]
        # Verify title banner
        self.assertEqual(ws.cell(row=1, column=1).value, "CRITICAL EQUIPMENT TELEMETRY AUDIT")
        # Verify headers row 3
        self.assertEqual(ws.cell(row=3, column=1).value, "Pump ID")
        self.assertEqual(ws.cell(row=3, column=2).value, "Vibration (mm/s)")
        # Verify data rows
        self.assertEqual(ws.cell(row=4, column=1).value, "P-101")
        # Verify summary formulas exist and are not plain values
        formula_found = False
        for row in ws.iter_rows(values_only=True):
            for val in row:
                if isinstance(val, str) and (val.startswith("=AVERAGE") or val.startswith("=MAX")):
                    formula_found = True
        self.assertTrue(formula_found, "Live Excel formula was not preserved in generated sheet")

    def test_read_nonexistent_spreadsheet(self):
        with self.assertRaises(FileNotFoundError):
            spreadsheet.read_spreadsheet("ghost_sheet_xyz.xlsx")


class TestDocgenTool(unittest.TestCase):
    def setUp(self):
        self.test_files = []

    def tearDown(self):
        for fname in self.test_files:
            p = os.path.join(files.WORKSPACE_DIR, fname)
            if os.path.exists(p):
                os.remove(p)

    def test_create_approval_note(self):
        filename = "boiler_overhaul_approval.docx"
        self.test_files.append(filename)

        findings_table = {
            "headers": ["Unit", "Observed Wall Thickness (mm)", "Min Permissible (mm)", "Compliance Status"],
            "rows": [
                ["Boiler Tube #14", "4.2", "4.0", "Compliant"],
                ["Boiler Tube #22", "3.6", "4.0", "NON-COMPLIANT (Erosion)"],
                ["Superheater Coil A", "5.1", "4.8", "Compliant"]
            ]
        }

        res = docgen.create_approval_note(
            filename=filename,
            title="Boiler Unit #4 Overhaul & Wall Thickness Clearance",
            reference_no="REF/ENG/2026/BOILER-04",
            department="Plant Engineering & Thermal Safety",
            author="Senior Inspector V. Kumar",
            background="Annual non-destructive ultrasonic testing of boiler pressure tubes.",
            findings=[
                "Ultrasonic thickness measurements performed across 48 sampling locations.",
                "Erosion detected on Tube #22 due to ash impaction.",
                "Primary pressure boundary remains within acceptable operating safety factor."
            ],
            findings_table=findings_table,
            risk_assessment="Continued operation of Tube #22 without pad welding risks localized puncture within 60 days.",
            recommendations=[
                "Immediate schedule pad weld repair on Tube #22 prior to recommissioning.",
                "Procure replacement alloy elbow section for Q3 overhaul.",
                "Grant conditional clearance for 45 days at 80% maximum rated steam capacity."
            ],
            signoff_name="Director of Engineering"
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "docx")
        self.assertTrue(os.path.exists(res["absolute_path"]))

        # Verify docx structure
        doc = Document(res["absolute_path"])
        full_text = "\n".join([p.text for p in doc.paragraphs])
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    full_text += "\n" + cell.text

        self.assertIn("OFFICIAL APPROVAL NOTE", full_text)
        self.assertIn("BOILER UNIT #4 OVERHAUL", full_text)
        self.assertIn("REF: REF/ENG/2026/BOILER-04", full_text)
        self.assertIn("Senior Inspector V. Kumar", full_text)
        self.assertIn("1. Background & Context", full_text)
        self.assertIn("2. Technical Observations & Findings", full_text)
        self.assertIn("3. Risk & Impact Assessment", full_text)
        self.assertIn("4. Proposed Recommendations & Next Steps", full_text)
        self.assertIn("NON-COMPLIANT (Erosion)", full_text)
        
        # Verify table presence
        self.assertGreaterEqual(len(doc.tables), 3) # meta table, findings table, signoff table

    def test_create_presentation(self):
        filename = "quarterly_inspection_deck.pptx"
        self.test_files.append(filename)

        slides = [
            {
                "title": "Executive Summary & Fleet Health",
                "bullets": [
                    "94% of critical assets operating within standard thermal parameters.",
                    "Turbine Unit 2 scheduled for vibration isolation retrofit.",
                    "Zero environmental or safety incidents in Q2."
                ]
            },
            {
                "title": "Corrective Action Timeline",
                "bullets": [
                    "Phase 1: Ultrasonic scans of feedwater lines (Completed).",
                    "Phase 2: Valve seal replacements across Section B (In Progress).",
                    "Phase 3: Final recommissioning sign-off by July 15."
                ]
            }
        ]

        res = docgen.create_presentation(
            filename=filename,
            title="Q2 Industrial Asset Integrity Review",
            subtitle="Air-Gapped Engineering Operations Directorate",
            slides=slides
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["type"], "pptx")
        self.assertEqual(res["slides_count"], 3) # Title slide + 2 bullet slides
        self.assertTrue(os.path.exists(res["absolute_path"]))

        # Verify pptx structure
        prs = Presentation(res["absolute_path"])
        self.assertEqual(len(prs.slides), 3)
        self.assertEqual(prs.slides[0].shapes.title.text, "Q2 Industrial Asset Integrity Review")
        self.assertEqual(prs.slides[1].shapes.title.text, "Executive Summary & Fleet Health")
        self.assertEqual(prs.slides[2].shapes.title.text, "Corrective Action Timeline")


if __name__ == "__main__":
    unittest.main()
