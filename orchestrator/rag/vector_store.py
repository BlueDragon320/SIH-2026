"""
Persistent Local Vector Store for Air-Gapped RAG using ChromaDB & Hybrid Search.
"""
import os
import re
import uuid
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from orchestrator.rag.embed import LocalEmbedder

logger = logging.getLogger("orchestrator.rag.vector_store")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_DIR = os.environ.get("CHROMA_DB_DIR", os.path.join(PROJECT_ROOT, "data", "chroma_db"))

class LocalVectorStore:
    def __init__(self, db_dir: str = DB_DIR):
        os.makedirs(db_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=db_dir, settings=Settings(anonymized_telemetry=False))
        self.embedder = LocalEmbedder()
        self.collection = self.client.get_or_create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into semantic paragraphs and token-sized chunks with overlap."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = []
        current_len = 0

        for p in paragraphs:
            p_clean = p.strip()
            if not p_clean:
                continue
            words = p_clean.split()
            if current_len + len(words) > chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    # Retain overlap words
                    overlap_words = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                    current_chunk = list(overlap_words)
                    current_len = len(current_chunk)
            current_chunk.extend(words)
            current_len += len(words)

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks if chunks else [text]

    def add_document(
        self,
        filename: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        sensitivity: Optional[str] = "internal",
        department: Optional[str] = "general"
    ) -> int:
        """Chunk, embed, and index a document into the vector store with sensitivity & department tags (Spec §5.6)."""
        chunks = self.chunk_text(text)
        if not chunks:
            return 0

        metadata = metadata or {}
        embeddings = self.embedder.embed_batch(chunks)
        ids = [f"{filename}_{uuid.uuid4().hex[:8]}_{i}" for i in range(len(chunks))]
        metadatas = []
        for i, _ in enumerate(chunks):
            m = dict(metadata)
            m["source"] = filename
            m["chunk_index"] = i
            m["total_chunks"] = len(chunks)
            m["sensitivity"] = metadata.get("sensitivity") or sensitivity or "internal"
            m["department"] = metadata.get("department") or department or "general"
            metadatas.append(m)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas
        )
        logger.info(f"Indexed document '{filename}': {len(chunks)} chunks stored (sensitivity={m['sensitivity']}, dept={m['department']}).")
        return len(chunks)

    def hybrid_search(
        self,
        query: str,
        top_k: int = 4,
        sensitivity: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search (cosine vector similarity + keyword BM25 boost) with optional sensitivity/department filters."""
        count = self.collection.count()
        if count == 0:
            return []

        query_embedding = self.embedder.embed_text(query)
        actual_k = min(top_k * 4 if (sensitivity or department) else top_k * 2, count)

        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"]
        )

        docs = vector_results.get("documents", [[]])[0]
        metadatas = vector_results.get("metadatas", [[]])[0]
        distances = vector_results.get("distances", [[]])[0]

        scored_results = []
        query_terms = set(re.findall(r"\w+", query.lower()))

        for doc, meta, dist in zip(docs, metadatas, distances):
            # Optional sensitivity and department filtering (Spec §5.6)
            if sensitivity and meta.get("sensitivity") != sensitivity:
                continue
            if department and meta.get("department") != department:
                continue

            # Cosine distance to similarity (1 - distance)
            sim_score = 1.0 - dist
            # Keyword presence boost
            doc_terms = set(re.findall(r"\w+", doc.lower()))
            overlap_count = len(query_terms.intersection(doc_terms))
            bm25_boost = (overlap_count / max(len(query_terms), 1)) * 0.25
            
            combined_score = sim_score + bm25_boost
            scored_results.append({
                "source": meta.get("source", "Unknown Document"),
                "chunk_index": meta.get("chunk_index", 0),
                "text": doc,
                "score": round(combined_score, 4),
                "metadata": meta
            })

        # Sort by combined score descending
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

    def list_indexed_documents(self) -> List[Dict[str, Any]]:
        """List distinct sources indexed in the vector store."""
        data = self.collection.get(include=["metadatas"])
        sources = {}
        for m in data.get("metadatas", []):
            if not m:
                continue
            src = m.get("source", "Unknown")
            sources[src] = sources.get(src, 0) + 1
        return [{"source": k, "chunks": v} for k, v in sources.items()]
