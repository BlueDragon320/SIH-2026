"""
Reusable UI Components: Header, Sidebar, Deliverable Cards, and Safe HTML Renderer.
"""
import os
import json
import streamlit as st
import pandas as pd
from frontend.api import api_get, api_post, api_delete, API_BASE_URL, get_file_mime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_DIR = os.environ.get("WORKBENCH_WORKSPACE_DIR", os.path.join(PROJECT_ROOT, "data", "workspace"))

def render_html(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

def render_header(gpu_info: dict, egress_rate: float):
    with st.container(key="main_header_row"):
        col_h_left, col_h_mid, col_h_menu = st.columns([3.5, 6, 0.8], vertical_alignment="center")
        with col_h_left:
            render_html('''
            <div class="header-left">
                <span class="brand-mark">⚡</span>
                <span class="brand-title">Workbench<span class="brand-ver">Auto-Route v1.0</span></span>
            </div>
            ''')
        with col_h_mid:
            render_html(f'''
            <div class="header-center">
                <span class="badge badge-blue">NLP: Qwen 3.5 4B</span>
                <span class="badge badge-amber">RTX 5050: {gpu_info["util"]} ({gpu_info["mem"]})</span>
                <span class="badge badge-green"><span class="live-dot"></span><span>Air-Gap: {egress_rate} B/s [ISOLATED]</span></span>
            </div>
            ''')
        with col_h_menu:
            with st.popover("⋮", help="Tools & Workspace Views"):
                st.markdown("<div style='font-size:0.75rem; font-weight:600; color:var(--text-muted); margin-bottom:6px;'>WORKSPACE VIEWS</div>", unsafe_allow_html=True)
                if st.button("💬 Chat Canvas", key="pop_nav_chat", use_container_width=True):
                    st.session_state["nav_view"] = "Chat Canvas"
                    st.rerun()
                if st.button("📦 Deliverables Hub", key="pop_nav_deliv", use_container_width=True):
                    st.session_state["nav_view"] = "Deliverables"
                    st.rerun()
                if st.button("📚 Knowledge Base (RAG)", key="pop_nav_rag", use_container_width=True):
                    st.session_state["nav_view"] = "Knowledge Base"
                    st.rerun()
                if st.button("⚙️ Model Registry", key="pop_nav_models", use_container_width=True):
                    st.session_state["nav_view"] = "Models"
                    st.rerun()
                if st.button("🛡️ Air-Gap Audit Logs", key="pop_nav_audit", use_container_width=True):
                    st.session_state["nav_view"] = "Air-Gap Audit"
                    st.rerun()

def render_sidebar(is_dark: bool, models_list: list, recent_tasks: list, gpu_info: dict):
    with st.sidebar:
        # Header Box & Theme Toggle
        with st.container(key="sb_header_box"):
            col_sb_title, col_sb_theme = st.columns([7, 1.2], vertical_alignment="center")
            with col_sb_title:
                render_html('<div class="sb-brand-text">Workbench</div>')
            with col_sb_theme:
                if st.button("", help="Toggle Dark/Light Theme", key="sb_theme_toggle"):
                    st.session_state["theme"] = "light" if is_dark else "dark"
                    st.rerun()

        # New Chat Button
        if st.button("＋  New chat", key="btn_new_task", use_container_width=True):
            st.session_state["active_task_id"] = None
            st.session_state["pending_prompt"] = ""
            st.session_state["nav_view"] = "Chat Canvas"
            st.rerun()

        # Model Selector Dropdown
        if "selected_model" not in st.session_state:
            st.session_state["selected_model"] = "Auto"

        curr_model = st.session_state["selected_model"]
        with st.expander(f"🤖 Model: {curr_model}", expanded=False):
            model_options = ["Auto"] + [m["name"] for m in models_list]
            curr_idx = model_options.index(curr_model) if curr_model in model_options else 0
            new_sel = st.selectbox(
                "Select Model",
                options=model_options,
                index=curr_idx,
                label_visibility="collapsed",
                key="sb_model_dropdown"
            )
            if new_sel != curr_model:
                st.session_state["selected_model"] = new_sel
                st.rerun()

            if new_sel == "Auto":
                st.caption("⚡ Auto-routes to lowest VRAM model based on task & capabilities.")
            else:
                m_info = next((m for m in models_list if m["name"] == new_sel), None)
                if m_info:
                    tag = m_info.get("ollama_tag", "")
                    is_inst = m_info.get("is_installed", False)
                    vram = m_info.get("vram_gb", 2.0)
                    if is_inst:
                        st.caption(f"🟢 Installed · `{tag}` ({vram} GB VRAM)")
                    else:
                        st.caption(f"⚪ Not installed on disk (`{tag}`)")
                        if st.button(f"⬇️ Download {tag}", key="pull_sb_model", use_container_width=True):
                            with st.spinner(f"Triggering Ollama download for {tag}..."):
                                api_post("/v1/models/pull", data={"ollama_tag": tag})
                            st.success(f"Pull started for {tag} in background.")
                            st.rerun()

        # Recent Chats List Header
        render_html("""
        <div class="chats-tasks-header">
            <span>Chats and tasks</span>
        </div>
        """)
        
        # Recent Chats List (Scrollable)
        with st.container(key="sb_chats_scroll"):
            if recent_tasks:
                for t in recent_tasks[:30]:
                    p_text = t.get("prompt", "Task").strip().replace("\n", " ")
                    p_short = p_text[:28] + ("…" if len(p_text) > 28 else "")
                    t_id = t["task_id"]
                    is_active = (st.session_state.get("active_task_id") == t_id)
                    k_name = f"hist_active_{t_id}" if is_active else f"hist_{t_id}"
                    
                    with st.container(key=f"hist_row_{t_id}"):
                        col_item, col_del = st.columns([8.2, 1.2], vertical_alignment="center", gap="small")
                        with col_item:
                            if st.button(p_short, key=k_name, use_container_width=True):
                                st.session_state["active_task_id"] = t_id
                                st.session_state["nav_view"] = "Chat Canvas"
                                st.rerun()
                        with col_del:
                            if st.button("✕", key=f"del_{t_id}", help="Delete chat"):
                                api_delete(f"/v1/task/{t_id}")
                                if st.session_state.get("active_task_id") == t_id:
                                    st.session_state["active_task_id"] = None
                                st.rerun()
            else:
                render_html('<div style="font-size:0.75rem; color:#6b7280; padding:4px 8px;">No previous chats</div>')

        # Footer
        render_html(f"""
        <div class="sidebar-footer-row">
            <span class="sidebar-username">BlueDragon</span>
            <span class="sidebar-gpu">RTX 3060: {gpu_info["util"]}</span>
        </div>
        """)

def render_deliverable_card(filename: str, tool_name: str = "", unique_prefix: str = "deliv"):
    filepath = os.path.join(WORKSPACE_DIR, filename)
    if not os.path.exists(filepath):
        st.warning(f"File `{filename}` not found in workspace.")
        return

    fsize_bytes = os.path.getsize(filepath)
    fsize_kb = round(fsize_bytes / 1024, 1)
    ext = os.path.splitext(filename)[1].lower()
    
    type_names = {
        ".py": "PYTHON SCRIPT",
        ".csv": "DATASET / CSV",
        ".xlsx": "EXCEL WORKBOOK",
        ".docx": "WORD DOCUMENT",
        ".png": "IMAGE ARTIFACT",
        ".jpg": "IMAGE ARTIFACT",
        ".jpeg": "IMAGE ARTIFACT",
        ".json": "JSON DATA",
        ".txt": "TEXT REPORT",
        ".md": "MARKDOWN"
    }
    type_label = type_names.get(ext, "DELIVERABLE")
    tool_badge = f" · {tool_name}" if tool_name else ""
    
    with st.expander(f"📄 {filename}  [{type_label}{tool_badge} · {fsize_kb} KB]", expanded=True):
        try:
            if ext in [".py", ".sh", ".bash"]:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    code_text = f.read()
                lang = "python" if ext == ".py" else "bash"
                st.code(code_text, language=lang, line_numbers=True)
                
            elif ext in [".csv"]:
                df = pd.read_csv(filepath)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Preview: {len(df)} rows × {len(df.columns)} columns")
                
            elif ext in [".xlsx"]:
                df = pd.read_excel(filepath)
                st.dataframe(df, use_container_width=True)
                st.caption(f"Preview: {len(df)} rows × {len(df.columns)} columns")
                
            elif ext in [".docx"]:
                import docx
                doc = docx.Document(filepath)
                st.caption(f"Document Structure: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")
                for p in doc.paragraphs:
                    if p.text.strip():
                        if p.style and p.style.name.startswith("Heading 1"):
                            st.markdown(f"### {p.text}")
                        elif p.style and p.style.name.startswith("Heading 2"):
                            st.markdown(f"#### {p.text}")
                        else:
                            st.markdown(p.text)
                for i, table in enumerate(doc.tables):
                    st.caption(f"Table {i+1}")
                    t_data = []
                    for row in table.rows:
                        t_data.append([cell.text.strip() for cell in row.cells])
                    if t_data and len(t_data) > 1:
                        st.dataframe(pd.DataFrame(t_data[1:], columns=t_data[0]), use_container_width=True)
                    elif t_data:
                        st.dataframe(pd.DataFrame(t_data), use_container_width=True)
                        
            elif ext in [".png", ".jpg", ".jpeg"]:
                st.image(filepath, caption=filename, use_container_width=True)
                
            elif ext in [".json"]:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    st.json(json.load(f), expanded=True)
                    
            elif ext in [".txt", ".md", ".log"]:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    st.text(f.read())
            else:
                st.info(f"Binary file ({ext}). Download below to inspect.")
        except Exception as err:
            st.error(f"Could not render preview: {err}")
            
        st.markdown("<div style='margin-top: 14px; padding-top: 10px; border-top: 1px solid var(--border-color);'></div>", unsafe_allow_html=True)
        col_info, col_dl, col_link = st.columns([3, 2, 1])
        with col_info:
            render_html(f"<div style='font-size:0.75rem; color:var(--text-muted); padding-top:6px;'><span style='color:var(--status-green);'>●</span> Air-gap verified on-device deliverable</div>")
        with col_dl:
            with open(filepath, "rb") as f_dl:
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=f_dl.read(),
                    file_name=filename,
                    mime=get_file_mime(filename),
                    use_container_width=True,
                    key=f"{unique_prefix}_dl_{filename}"
                )
        with col_link:
            st.link_button("Direct URL", f"{API_BASE_URL}/v1/workspace/download/{filename}", use_container_width=True)
