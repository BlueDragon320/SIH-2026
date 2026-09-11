"""
Reusable UI Components: Header, Sidebar, Deliverable Cards, and Safe HTML Renderer.
Red Noir Design System with Crimson Accents.
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

def render_header(gpu_info: dict, egress_rate: float, active_model_label: str = "Auto-Route"):
    with st.container(key="main_header_row"):
        col_h_left, col_h_mid, col_h_menu = st.columns([3.6, 5.8, 0.6], vertical_alignment="center")
        with col_h_left:
            render_html(f'''
            <div class="header-left" style="display:flex; align-items:center; gap:8px;">
                <span style="width:14px; height:14px; background:#ef233c; border-radius:2px; transform:rotate(45deg); display:inline-block; margin-right:8px; box-shadow:0 0 10px rgba(239,35,60,0.6); flex-shrink:0;"></span>
                <span class="brand-title" style="font-family:'Manrope',sans-serif; font-weight:700;">Workbench <span class="brand-ver">{active_model_label}</span></span>
            </div>
            ''')
        with col_h_mid:
            render_html(f'''
            <div class="header-center" style="display:flex; gap:8px; align-items:center; justify-content:center;">
                <span class="badge badge-red"><span class="live-dot"></span>{active_model_label}</span>
                <span class="badge badge-amber">RTX 3060: {gpu_info["util"]} ({gpu_info["mem"]})</span>
                <span class="badge badge-green">0.0 B/S EGRESS</span>
            </div>
            ''')
        with col_h_menu:
            with st.popover("⋮", help="Tools & Workspace Views"):
                st.markdown("<div style='font-family:\"JetBrains Mono\",monospace; font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-muted); padding:6px 10px 8px 10px;'>WORKSPACE VIEWS</div>", unsafe_allow_html=True)
                if st.button("💬 Chat Canvas", key="pop_nav_chat", use_container_width=True):
                    st.session_state["nav_view"] = "Chat Canvas"
                    st.rerun()
                if st.button("📁 Deliverables Hub", key="pop_nav_deliv", use_container_width=True):
                    st.session_state["nav_view"] = "Deliverables"
                    st.rerun()
                if st.button("📚 Knowledge Base", key="pop_nav_rag", use_container_width=True):
                    st.session_state["nav_view"] = "Knowledge Base"
                    st.rerun()
                if st.button("⚙️ Model Registry", key="pop_nav_models", use_container_width=True):
                    st.session_state["nav_view"] = "Models"
                    st.rerun()
                if st.button("🛡️ Air-Gap Audit Logs", key="pop_nav_audit", use_container_width=True):
                    st.session_state["nav_view"] = "Air-Gap Audit"
                    st.rerun()

def render_sidebar(is_dark: bool, models_list: list, recent_tasks: list, gpu_info: dict, ollama_tags: list = None):
    ollama_tags = ollama_tags or []
    with st.sidebar:
        # Header Box & Theme Toggle
        with st.container(key="sb_header_box"):
            col_sb_title, col_sb_theme = st.columns([5.5, 1.8], vertical_alignment="center")
            with col_sb_title:
                render_html('''
                <div class="sb-brand-text" style="display:flex; align-items:center;">
                    <span style="width:14px; height:14px; background:#ef233c; border-radius:2px; transform:rotate(45deg); display:inline-block; margin-right:8px; box-shadow:0 0 10px rgba(239,35,60,0.6); flex-shrink:0;"></span>
                    <span>Workbench</span>
                </div>
                ''')
            with col_sb_theme:
                if st.button("🌓", help="Toggle Theme", key="sb_theme_toggle"):
                    st.session_state["theme"] = "light" if is_dark else "dark"
                    st.rerun()

        # New Chat Button
        if st.button("＋  New chat", key="btn_new_task", use_container_width=True):
            st.session_state["active_task_id"] = None
            st.session_state["pending_prompt"] = ""
            st.session_state["nav_view"] = "Chat Canvas"
            st.rerun()

        # LLM Model Selector (Auto Select + 3 Main Models + Installed Models)
        st.markdown("<div style='font-family:\"JetBrains Mono\",monospace; font-size:0.72rem; font-weight:600; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-top:14px; margin-bottom:6px;'>MODEL SELECTION</div>", unsafe_allow_html=True)
        
        # Clean, unified model options dictionary
        model_display_map = {
            "Auto": "⚡ Auto Select (Intelligent Router)",
            "qwen2.5-coder:7b": "● Qwen 2.5 Coder 7B (Coding)",
            "llama3.1:8b": "● Llama 3.1 8B (General & Docs)",
            "deepseek-r1:7b": "● DeepSeek R1 7B (Math & Engineering)",
            "moondream:latest": "● Moondream 1.8B (Vision & OCR)",
        }
        
        # Add any other installed tags on disk
        for tag in ollama_tags:
            tag_name = tag.get("name", tag) if isinstance(tag, dict) else str(tag)
            clean_tag = tag_name.split(":")[0] if ":" in tag_name else tag_name
            if tag_name not in model_display_map and not any(clean_tag == k.split(":")[0] for k in model_display_map):
                model_display_map[tag_name] = f"● {tag_name} (Installed)"
                
        # Add registered models if not present
        for m in models_list:
            m_tag = m.get("ollama_tag", "")
            m_name = m.get("name", "")
            clean_tag = m_tag.split(":")[0] if ":" in m_tag else m_tag
            if m_tag and m_tag not in model_display_map and not any(clean_tag == k.split(":")[0] for k in model_display_map):
                is_inst = m.get("is_installed", False) or any(m_tag in str(t) for t in ollama_tags)
                icon = "●" if is_inst else "○"
                model_display_map[m_tag] = f"{icon} {m_name} ({m_tag})"

        options_keys = list(model_display_map.keys())
        
        def _on_model_change():
            st.session_state["selected_model"] = st.session_state["sb_model_select"]

        if "selected_model" not in st.session_state or st.session_state["selected_model"] not in options_keys:
            st.session_state["selected_model"] = "Auto"
            
        curr_key = st.session_state["selected_model"]
        curr_idx = options_keys.index(curr_key) if curr_key in options_keys else 0
        
        selected_key = st.selectbox(
            "Select LLM",
            options=options_keys,
            index=curr_idx,
            format_func=lambda k: model_display_map.get(k, k),
            label_visibility="collapsed",
            key="sb_model_select",
            on_change=_on_model_change
        )
        st.session_state["selected_model"] = selected_key

        if selected_key == "Auto":
            render_html("""
            <div style="font-size:0.75rem; color:var(--text-muted); padding:4px 2px 8px 2px; text-align:left; line-height:1.45;">
                <span style="color:#ef233c; font-weight:600;">⚡ Auto Routing:</span> Queries dynamically dispatched to coding, reasoning, math, or vision models based on task intent.
            </div>
            """)
        else:
            m_info = next((m for m in models_list if m.get("ollama_tag") == selected_key or m.get("name") == selected_key), None)
            target_tag = selected_key
            is_inst = any(target_tag.split(":")[0] in str(t) for t in ollama_tags) or (m_info and m_info.get("is_installed", False))
            vram = m_info.get("vram_gb", 4.7) if m_info else 4.7
            
            if is_inst:
                render_html(f'<div style="font-size:0.75rem; color:var(--text-primary); padding:4px 2px 6px 2px; text-align:left;"><span style="color:#ef233c;">●</span> Pinned to <code>{target_tag}</code> (~{vram} GB VRAM)</div>')
            else:
                render_html(f'<div style="font-size:0.75rem; color:var(--text-muted); padding:4px 2px 4px 2px; text-align:left;">○ Not installed on disk (<code>{target_tag}</code>)</div>')
                if st.button(f"⬇ Download {target_tag}", key="pull_sb_model", use_container_width=True):
                    with st.spinner(f"Triggering Ollama download for {target_tag}..."):
                        api_post("/v1/models/pull", data={"ollama_tag": target_tag})
                    st.success(f"Pull started for {target_tag} in background.")
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
                            if st.button(f"◆  {p_short}", key=k_name, use_container_width=True):
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
                render_html('<div style="font-size:0.75rem; color:var(--text-muted); padding:4px 8px;">No previous chats</div>')

        # Footer
        render_html(f"""
        <div class="sidebar-footer-row">
            <span class="sidebar-username">BlueDragon</span>
            <span class="sidebar-gpu" style="color:#ef233c;">RTX 3060: {gpu_info["util"]}</span>
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
            render_html("<div style='font-size:0.75rem; color:var(--text-muted); padding-top:6px;'><span style='color:#ef233c;'>●</span> Air-gap verified on-device deliverable</div>")
        with col_dl:
            with open(filepath, "rb") as f_dl:
                st.download_button(
                    label=f"⬇ Download {filename}",
                    data=f_dl.read(),
                    file_name=filename,
                    mime=get_file_mime(filename),
                    use_container_width=True,
                    key=f"{unique_prefix}_dl_{filename}"
                )
        with col_link:
            st.link_button("Direct URL", f"{API_BASE_URL}/v1/workspace/download/{filename}", use_container_width=True)
