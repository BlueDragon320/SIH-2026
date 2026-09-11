"""
Deliverables Hub View: Workspace deliverables and generated files preview.
"""
import streamlit as st
from frontend.api import api_get
from frontend.components import render_html, render_deliverable_card

def render_deliverables_view():
    render_html("""
    <div class="section-header">
        <h2>Workspace Deliverables</h2>
        <p>Sandboxed office artifacts, spreadsheets, and code deliverables generated on-device.</p>
    </div>
    """)

    files_list = api_get("/v1/workspace/files") or []
    if files_list:
        for idx, f in enumerate(files_list):
            fname = f["filename"]
            render_deliverable_card(fname, unique_prefix=f"hub_{idx}")
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
    else:
        st.info("Workspace is empty. Run a task on Chat Canvas to generate files.")
