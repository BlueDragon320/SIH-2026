"""
Chat Canvas View: Supports Multi-Turn Thread Persistence, Suggestion Cards, and Left-Aligned Chat Input.
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
        <div class="hero-container" style="text-align: center; margin: 2.5rem 0 2rem 0;">
            <h1 class="hero-title" style="font-size: 2.1rem; font-weight: 600; letter-spacing: -0.025em; color: var(--text-primary); margin-bottom: 0.5rem;">What would you like to build?</h1>
            <p class="hero-subtitle" style="font-size: 0.95rem; color: var(--text-muted);">Air-gapped on-premises intelligence · Zero external network calls</p>
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
                        "model": task_data.get("ollama_tag", "qwen3.5:4b"),
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
                        model_tag = msg.get("model") or task_data.get("ollama_tag", "qwen3.5:4b")
                        task_cat = msg.get("task_type") or task_data.get("task_type", "general_qa")
                        steps = msg.get("steps", [])
                        delivs = msg.get("deliverables", [])

                        render_html(f"""
                        <div style="display:flex; gap:8px; margin-bottom:12px; align-items:center;">
                            <span class="badge badge-blue">MODEL: {model_tag}</span>
                            <span class="badge badge-amber">TASK: {task_cat}</span>
                            <span class="badge badge-green"><span class="live-dot"></span>AIR-GAP: VERIFIED</span>
                        </div>
                        """)

                        if steps:
                            with st.expander(f"Execution Step Trace ({len(steps)} steps completed)", expanded=False):
                                for s in steps:
                                    if isinstance(s, dict):
                                        st.markdown(f"**Step {s.get('step_number')} [{s.get('phase')}]:** {s.get('description')}")
                                        if s.get("tool_name"):
                                            st.caption(f"Invoked Tool: `{s.get('tool_name')}`")
                                        if s.get("tool_output") and isinstance(s.get("tool_output"), dict):
                                            out_dict = s.get("tool_output")
                                            if out_dict.get("stdout"):
                                                st.caption("Console Output:")
                                                st.code(out_dict["stdout"], language="text")
                                            elif out_dict.get("status"):
                                                st.caption(f"Status: `{out_dict.get('status')}`")

                        if content and content.strip():
                            st.markdown(content)

                        if delivs:
                            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
                            render_html('<div style="font-size: 0.74rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 8px;">GENERATED DELIVERABLES & OUTPUT PREVIEW</div>')
                            for idx, d in enumerate(delivs):
                                fname = d.get("name") if isinstance(d, dict) else str(d)
                                t_name = d.get("tool", "") if isinstance(d, dict) else ""
                                render_deliverable_card(fname, tool_name=t_name, unique_prefix=f"chat_{active_task_id}_{turn_idx}_{idx}")

            # If task is currently running, display live loading banner and auto-poll
            if t_status == "RUNNING":
                with st.chat_message("assistant"):
                    render_html("""
                    <div style="display:flex; align-items:center; gap:10px; padding:12px 16px; background:var(--bg-card); border:1px solid var(--border-color); border-radius:10px; margin-top:8px;">
                        <span style="font-size:1.2rem; animation: pulse 1.5s infinite; color:var(--accent-amber);">⚡</span>
                        <span style="font-size:0.88rem; color:var(--text-primary); font-weight:500;">Qwen 3.5 is generating response...</span>
                    </div>
                    """)
                    time.sleep(1.2)
                    st.rerun()

    # -------------------------------------------------------------
    # BOTTOM FLOATING CHAT INPUT SECTION
    # -------------------------------------------------------------
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    incoming_prompt = st.session_state.pop("pending_prompt", "")

    with st.expander("Attach Document / Drawing / Dataset", expanded=False):
        uploaded_files = st.file_uploader(
            "Upload files",
            type=["png", "jpg", "jpeg", "pdf", "docx", "csv", "txt"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

    chat_input_val = st.chat_input("Message Workbench...")
    target_prompt = chat_input_val or incoming_prompt

    if target_prompt:
        attachment_names = []
        if uploaded_files:
            for uf in uploaded_files:
                up_res = api_post("/v1/workspace/upload", files={"file": (uf.name, uf.getvalue())})
                if "filename" in up_res:
                    attachment_names.append(up_res["filename"])

        # Override model selection if chosen in sidebar
        sb_model = st.session_state.get("selected_model", "Auto")
        override_val = None if sb_model == "Auto" else sb_model
        
        # Submit prompt to existing active_task_id or start new chat session
        res = api_post("/v1/task", data={
            "prompt": target_prompt,
            "attachments": attachment_names,
            "manual_model_override": override_val,
            "task_id": active_task_id if active_task_id else None
        })

        if res and "task_id" in res:
            st.session_state["active_task_id"] = res["task_id"]
            st.rerun()

    render_html("""
    <div class="disclaimer">
        Air-Gapped Autonomous Workbench · Model can make mistakes · Verify critical engineering outputs
    </div>
    """)
