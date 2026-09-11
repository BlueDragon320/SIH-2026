"""
Knowledge Base View: Air-gapped ChromaDB vector store and RAG document search/ingest.
"""
import streamlit as st
import pandas as pd
from frontend.api import api_get, api_post
from frontend.components import render_html

def render_knowledge_base_view():
    render_html("""
    <div class="section-header">
        <h2>Knowledge Base</h2>
        <p>Air-gapped ChromaDB vector store with semantic embeddings via local nomic-embed-text.</p>
    </div>
    """)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("##### Search Knowledge Base")
        rag_query = st.text_input("Search query", placeholder="Search turbine limits, SOP-04, procurement rules...", label_visibility="collapsed")
        if rag_query:
            srch = api_post("/v1/tools/rag_search/invoke", data={"tool_args": {"query": rag_query, "top_k": 3}})
            if srch and "citations" in srch:
                st.markdown(srch.get("formatted_text", "No matches."))
            else:
                st.info("No matching citations found.")
        
        st.markdown("---")
        st.markdown("##### Indexed Documents")
        kb_docs = api_get("/v1/knowledge-base/documents") or []
        if kb_docs:
            st.dataframe(pd.DataFrame(kb_docs), use_container_width=True, hide_index=True)
        else:
            st.caption("No indexed documents.")

    with col2:
        st.markdown("##### Ingest SOP / Manual")
        kb_file = st.file_uploader("Upload SOP (.md, .txt, .pdf, .docx)", type=["md", "txt", "pdf", "docx"], label_visibility="collapsed")
        if kb_file and st.button("Ingest Document", use_container_width=True):
            with st.spinner("Chunking & embedding..."):
                ing = api_post("/v1/knowledge-base/ingest", files={"file": (kb_file.name, kb_file.getvalue())})
                st.success(ing.get("message", "Ingestion complete."))
                st.rerun()
