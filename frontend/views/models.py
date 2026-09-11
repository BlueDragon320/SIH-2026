"""
Models View: Model registry and zero-downtime model registration.
"""
import streamlit as st
import pandas as pd
from frontend.api import api_get, api_post
from frontend.components import render_html

def render_models_view(models_list: list):
    render_html("""
    <div class="section-header">
        <h2>Models & Hardware</h2>
        <p>Manage open-weight models and dynamically register new models without server restarts.</p>
    </div>
    """)

    if models_list:
        df_m = pd.DataFrame(models_list)[["name", "ollama_tag", "capabilities", "vram_gb", "is_installed", "is_resident"]]
        st.dataframe(df_m, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("##### Register New Model (Zero Downtime)")
    with st.form("reg_form"):
        r_name = st.text_input("Model Name", placeholder="e.g. specialized-qa")
        r_tag = st.text_input("Ollama Tag", placeholder="e.g. phi3:mini")
        r_caps = st.multiselect("Capabilities", ["code_gen", "doc_draft", "vision_ocr", "spreadsheet_calc", "general_qa", "multi_step_plan", "embedding"], default=["general_qa"])
        r_vram = st.number_input("VRAM Budget (GB)", value=2.2, step=0.5)
        r_ctx = st.number_input("Context Window", value=32768, step=4096)
        
        if st.form_submit_button("Register Model", use_container_width=True):
            if r_name and r_tag:
                api_post("/v1/models/register", data={
                    "name": r_name,
                    "ollama_tag": r_tag,
                    "capabilities": r_caps,
                    "vram_gb": r_vram,
                    "context_window": r_ctx
                })
                st.success(f"Model '{r_name}' registered successfully.")
                st.rerun()
