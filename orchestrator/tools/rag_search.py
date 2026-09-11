"""
RAG Search Tool for Air-Gapped Agentic Workbench.
Queries the local ChromaDB vector store and formats citations.
"""
from typing import List, Dict, Any
from orchestrator.rag.vector_store import LocalVectorStore

_store_instance = None

def get_vector_store() -> LocalVectorStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = LocalVectorStore()
    return _store_instance

def search_knowledge_base(query: str, top_k: int = 4) -> Dict[str, Any]:
    """
    Search the local air-gapped knowledge base for relevant SOPs, manuals, or documents.
    Returns excerpts with exact document citations.
    """
    store = get_vector_store()
    results = store.hybrid_search(query=query, top_k=top_k)
    
    if not results:
        return {
            "query": query,
            "results_count": 0,
            "citations": [],
            "formatted_text": "No matching documents found in the local knowledge base."
        }

    formatted_sections = []
    citations = []

    for idx, r in enumerate(results, 1):
        source = r["source"]
        chunk_idx = r["chunk_index"]
        score = r["score"]
        text = r["text"]
        
        citations.append({
            "citation_id": f"[{idx}]",
            "source": source,
            "chunk_index": chunk_idx,
            "relevance_score": score
        })
        
        formatted_sections.append(
            f"--- Citation [{idx}] (Source: {source}, Chunk #{chunk_idx}, Relevance: {score}) ---\n{text}"
        )

    return {
        "query": query,
        "results_count": len(results),
        "citations": citations,
        "formatted_text": "\n\n".join(formatted_sections)
    }
