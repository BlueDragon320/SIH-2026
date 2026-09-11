"""
Chat Canvas View: Supports Multi-Turn Thread Persistence, Suggestion Cards, and Left-Aligned Chat Input.
Red Noir Design System with Crimson Accents.
"""
import time
import streamlit as st
from frontend.api import api_get, api_post
from frontend.components import render_html, render_deliverable_card

def render_chat_view():
    active_task_id = st.session_state.get("active_task_id")

    # Empty State (Hero Section & Suggestion Cards)
    if not active_task_id:
        render_html("""
        <div class="hero-container">
            <h1 class="hero-title">Design & Engineering Intelligence for <span class="text-red">Air-Gapped Operations</span></h1>
            <p class="hero-subtitle">Air-Gapped Autonomous Intelligence · Zero External Egress</p>
        </div>
        """)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button(
                "**Python Sandbox Code**\nValidate industrial sensor telemetry against tolerance limits in isolated sandbox",
                key="card_py",
                use_container_width=True
            ):
                st.session_state["pending_prompt"] = "Write a Python script to validate industrial sensor readings against tolerance limits and execute it in the isolated sandbox."
                st.rerun()

            if st.button(
                "**Audited Spreadsheet (.xlsx)**\nGenerate component tolerance workbook with live formulas for SUM and AVERAGE",
                key="card_sheet",
                use_container_width=True
            ):
                st.session_state["pending_prompt"] = "Create an Excel spreadsheet calculating component tolerance deviations with live formulas for SUM and AVERAGE."
                st.rerun()

        with col_c2:
            if st.button(
                "**Metrology Scan to .docx**\nIngest turbine inspection scan, extract findings, and draft formal Approval Note",
                key="card_doc",
                use_container_width=True
            ):
                st.session_state["pending_prompt"] = "Review the turbine stage metrology readings, verify tolerance compliance against ISO standards, and draft an Official Approval Note (.docx)."
                st.rerun()

            if st.button(
                "**SOP Knowledge Search (RAG)**\nSearch local ChromaDB knowledge base for turbine vibration and temperature limits",
                key="card_rag",
                use_container_width=True
            ):
                st.session_state["pending_prompt"] = "Search the local knowledge base for turbine blade vibration thresholds and maximum temperature limits per SOP-04."
                st.rerun()

    # Active Conversation Thread View (Multi-Turn Chat History)
    else:
        task_data = api_get(f"/v1/task/{active_task_id}")
        if task_data:
            t_status = task_data.get("status", "RUNNING")
            messages = task_data.get("messages", [])

            # Fallback if messages array is empty in old backend format
            if not messages:
                if task_data.get("prompt"):
                    messages.append({"role": "user", "content": task_data.get("prompt")})
                if task_data.get("final_response"):
                    messages.append({
                        "role": "assistant",
                        "content": task_data.get("final_response"),
                        "steps": task_data.get("steps", []),
                        "deliverables": task_data.get("deliverables", []),
                        "model": task_data.get("ollama_tag", "local-model"),
                        "task_type": task_data.get("task_type", "general_qa")
                    })

            # Render full chronological conversation thread
            for turn_idx, msg in enumerate(messages):
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                        atts = msg.get("attachments", [])
                        if atts:
                            st.caption(f"📎 Attached: {', '.join(atts)}")

                elif role == "assistant":
                    with st.chat_message("assistant"):
                        model_tag = msg.get("model") or task_data.get("ollama_tag") or "local-model"
                        task_cat = msg.get("task_type") or task_data.get("task_type", "general_qa")
                        steps = msg.get("steps", [])
                        delivs = msg.get("deliverables", [])

                        render_html(f"""
                        <div style="display:flex; gap:8px; margin-bottom:14px; align-items:center; flex-wrap:wrap;">
                            <span class="badge badge-red"><span class="live-dot"></span>MODEL: {model_tag}</span>
                            <span class="badge badge-amber">TASK: {task_cat}</span>
                            <span class="badge badge-green">AIR-GAP: VERIFIED</span>
                        </div>
                        """)

                        if steps:
                            with st.expander(f"⚙️ Execution Steps ({len(steps)} actions)", expanded=False):
                                for s in steps:
                                    if isinstance(s, dict):
                                        st.markdown(f"**Step {s.get('step_number')} [{s.get('phase')}]:** {s.get('description')}")
                                        if s.get("tool_name"):
                                            st.caption(f"Invoked Tool: `{s.get('tool_name')}`")
                                        if s.get("tool_output") and isinstance(s.get("tool_output"), dict):
                                            out_dict = s.get("tool_output")
                                            if out_dict.get("stdout"):
                                                st.code(out_dict.get("stdout"), language="bash")
                                            if out_dict.get("error"):
                                                st.error(out_dict.get("error"))
                                    st.markdown("---")

                        if content:
                            st.markdown(content)

                        if delivs:
                            st.markdown("<div style='margin-top:1.4rem;'></div>", unsafe_allow_html=True)
                            render_html('<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-bottom:10px;">GENERATED DELIVERABLES & OUTPUT PREVIEW</div>')
                            for idx, d in enumerate(delivs):
                                fname = d.get("name") if isinstance(d, dict) else str(d)
                                t_name = d.get("tool", "") if isinstance(d, dict) else ""
                                render_deliverable_card(fname, tool_name=t_name, unique_prefix=f"t{turn_idx}_{idx}")

            # If task is currently running, display live loading banner and auto-poll
            if t_status == "RUNNING":
                with st.chat_message("assistant"):
                    running_model = task_data.get("ollama_tag") or st.session_state.get("selected_model", "Local LLM")
                    render_html(f"""
                    <div style="display:flex; align-items:center; gap:12px; padding:14px 18px; background:var(--bg-card); border:1px solid rgba(239, 35, 60, 0.4); border-radius:12px; margin-top:8px; box-shadow: 0 0 16px rgba(239, 35, 60, 0.15);">
                        <span class="live-dot"></span>
                        <span style="font-family:'Manrope',sans-serif; font-size:0.95rem; font-weight:500; color:var(--text-primary);"><span style="color:#ef233c; font-weight:700;">{running_model}</span> is reasoning & generating deliverable...</span>
                    </div>
                    """)
                    time.sleep(1.2)
                    st.rerun()

    # -------------------------------------------------------------
    # BOTTOM FLOATING CHAT INPUT SECTION
    # -------------------------------------------------------------
    incoming_prompt = st.session_state.pop("pending_prompt", "")
    chat_input_val = st.chat_input(
        "Write a message...",
        accept_file="multiple",
        file_type=[
            "txt", "md", "markdown", "pdf", "docx", "csv", "xlsx", "xls",
            "json", "yaml", "yml", "log", "py", "sh", "sql",
            "png", "jpg", "jpeg", "webp", "bmp"
        ]
    )

    target_prompt = None
    uploaded_files = []
    if chat_input_val:
        if hasattr(chat_input_val, "text"):
            target_prompt = chat_input_val.text
            uploaded_files = getattr(chat_input_val, "files", []) or []
        elif isinstance(chat_input_val, dict):
            target_prompt = chat_input_val.get("text", "")
            uploaded_files = chat_input_val.get("files", []) or []
        else:
            target_prompt = str(chat_input_val)

    if incoming_prompt and not target_prompt:
        target_prompt = incoming_prompt

    if target_prompt or uploaded_files:
        with st.spinner("Processing request..."):
            attachment_names = []
            if uploaded_files:
                for uf in uploaded_files:
                    up_res = api_post("/v1/workspace/upload", files={"file": (uf.name, uf.getvalue())})
                    if "filename" in up_res:
                        attachment_names.append(up_res["filename"])

            # Override model selection if chosen in sidebar
            sb_model = st.session_state.get("selected_model") or st.session_state.get("sb_model_select") or "Auto"
            override_val = None if sb_model == "Auto" else sb_model
            
            # Submit prompt to existing active_task_id or start new chat session
            res = api_post("/v1/task", data={
                "prompt": target_prompt or "Attached files inspection",
                "attachments": attachment_names,
                "manual_model_override": override_val,
                "task_id": active_task_id if active_task_id else None
            })

            if res and "task_id" in res:
                st.session_state["active_task_id"] = res["task_id"]
                st.rerun()

    render_html("""
    <div class="disclaimer">
        Workbench operates in 100% on-premises air-gap mode. Code execution is isolated in secure sandbox.
    </div>
    """)
