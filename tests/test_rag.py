"""
Tests for Air-Gapped Local Knowledge Base / RAG:
- embed.py: Local embeddings client & deterministic air-gap fallback
- vector_store.py: Document chunking, indexing, and hybrid retrieval with citations
- rag_search.py: RAG search tool integration with structured citation formatting
"""
import unittest
import os
import tempfile
import shutil
from orchestrator.rag.embed import LocalEmbedder
from orchestrator.rag.vector_store import LocalVectorStore
from orchestrator.tools import rag_search

class TestLocalEmbedder(unittest.TestCase):
    def setUp(self):
        self.embedder = LocalEmbedder()

    def test_embed_text(self):
        text = "Standard Operating Procedure for High-Pressure Steam Turbine Safety."
        vec = self.embedder.embed_text(text)
        self.assertIsInstance(vec, list)
        self.assertGreater(len(vec), 0)
        self.assertTrue(all(isinstance(x, float) for x in vec))

    def test_embed_batch(self):
        texts = [
            "Boiler inspection tolerance guidelines.",
            "Emergency shutdown protocol for cooling towers.",
            "Bearing vibration threshold analysis."
        ]
        batch_vecs = self.embedder.embed_batch(texts)
        self.assertEqual(len(batch_vecs), 3)
        for v in batch_vecs:
            self.assertIsInstance(v, list)
            self.assertGreater(len(v), 0)


class TestLocalVectorStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vector_store = LocalVectorStore(db_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_chunk_text(self):
        # Create a document with multiple paragraphs
        para1 = "Paragraph 1: " + " ".join([f"word{i}" for i in range(200)])
        para2 = "Paragraph 2: " + " ".join([f"token{i}" for i in range(250)])
        para3 = "Paragraph 3: " + " ".join([f"item{i}" for i in range(300)])
        full_text = f"{para1}\n\n{para2}\n\n{para3}"

        chunks = self.vector_store.chunk_text(full_text, chunk_size=200, overlap=30)
        self.assertGreaterEqual(len(chunks), 3)
        for c in chunks:
            self.assertGreater(len(c), 0)

    def test_add_document_and_list(self):
        doc1_text = """
        SOP-2026-ENG-09: Hydraulic Pressure Relief Valve Calibration
        1. Purpose: Establish calibration routines for main boiler hydraulic lines.
        2. Set Point: Primary relief valve must actuate at precisely 120.5 bar +/- 0.5 bar.
        3. Inspection Frequency: Ultrasonic leak check every 90 operational days.
        """
        doc2_text = """
        SOP-2026-ENG-14: Steam Turbine Vibration Limits
        1. Purpose: Define allowable vibration amplitudes on turbine shaft bearings.
        2. Normal Limit: RMS velocity <= 2.8 mm/s.
        3. Trip Limit: RMS velocity >= 7.1 mm/s initiates emergency trip.
        """

        added1 = self.vector_store.add_document(
            filename="sop_hydraulic_valve.md",
            text=doc1_text,
            metadata={"category": "safety", "rev": "2.1"}
        )
        self.assertGreater(added1, 0)

        added2 = self.vector_store.add_document(
            filename="sop_turbine_vibration.md",
            text=doc2_text,
            metadata={"category": "operations", "rev": "1.4"}
        )
        self.assertGreater(added2, 0)

        docs = self.vector_store.list_indexed_documents()
        sources = [d["source"] for d in docs]
        self.assertIn("sop_hydraulic_valve.md", sources)
        self.assertIn("sop_turbine_vibration.md", sources)

    def test_hybrid_search_with_citations(self):
        doc_valve = """
        SOP-2026-ENG-09: Hydraulic Pressure Relief Valve Calibration
        Primary relief valve setpoint must actuate at 120.5 bar.
        Inspection frequency is every 90 days.
        """
        doc_turbine = """
        SOP-2026-ENG-14: Steam Turbine Vibration Limits
        Normal bearing vibration limit is 2.8 mm/s RMS.
        Emergency trip occurs when vibration exceeds 7.1 mm/s RMS.
        """
        self.vector_store.add_document("sop_valve.md", doc_valve)
        self.vector_store.add_document("sop_turbine.md", doc_turbine)

        # Search specifically for turbine vibration
        results = self.vector_store.hybrid_search("turbine vibration bearing trip limit", top_k=2)
        self.assertGreater(len(results), 0)
        top_result = results[0]

        self.assertEqual(top_result["source"], "sop_turbine.md")
        self.assertIn("source", top_result)
        self.assertIn("chunk_index", top_result)
        self.assertIn("score", top_result)
        self.assertIn("text", top_result)
        self.assertIn("metadata", top_result)
        self.assertIn("7.1 mm/s", top_result["text"])

        # Search specifically for valve pressure
        valve_results = self.vector_store.hybrid_search("hydraulic relief valve setpoint bar", top_k=2)
        self.assertGreater(len(valve_results), 0)
        self.assertEqual(valve_results[0]["source"], "sop_valve.md")
        self.assertIn("120.5 bar", valve_results[0]["text"])

    def test_empty_search(self):
        # Empty collection search should return empty list gracefully
        empty_store = LocalVectorStore(db_dir=os.path.join(self.temp_dir.name, "empty_db"))
        res = empty_store.hybrid_search("anything")
        self.assertEqual(res, [])


class TestRagSearchTool(unittest.TestCase):
    def test_search_knowledge_base_formatting(self):
        # Ingest a sample doc into global store or test tool formatting
        res = rag_search.search_knowledge_base("safety inspection guidelines", top_k=3)
        self.assertIn("query", res)
        self.assertIn("results_count", res)
        self.assertIn("citations", res)
        self.assertIn("formatted_text", res)
        self.assertIsInstance(res["citations"], list)


if __name__ == "__main__":
    unittest.main()
