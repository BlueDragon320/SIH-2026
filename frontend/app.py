"""
Air-Gapped Agentic AI Workbench - Modular Streamlit Main Application Entry Point.
"""
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from frontend.styles import inject_global_css
from frontend.api import api_get, get_gpu_telemetry
from frontend.components import render_header, render_sidebar
from frontend.views.chat import render_chat_view
from frontend.views.deliverables import render_deliverables_view
from frontend.views.knowledge_base import render_knowledge_base_view
from frontend.views.models import render_models_view
from frontend.views.audit import render_audit_view

# Page Config
st.set_page_config(
    page_title="Workbench Auto-Route v1.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Theme State
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
is_dark = (st.session_state["theme"] == "dark")

# Inject Design System & Custom CSS
inject_global_css(is_dark)

# Fetch System Telemetry
gpu_info = get_gpu_telemetry()
net_status = api_get("/v1/network-status") or {}
egress_rate = net_status.get("external_egress_rate_bps", 0.0)
models_data = api_get("/v1/models") or {}
models_list = models_data.get("models", [])
recent_tasks = api_get("/v1/tasks") or []

# Navigation View State
if "nav_view" not in st.session_state:
    st.session_state["nav_view"] = "Chat Canvas"
nav_view = st.session_state["nav_view"]

# Render Global Header & Sidebar
render_header(gpu_info, egress_rate)
render_sidebar(is_dark, models_list, recent_tasks, gpu_info)

# Render Target View
if nav_view == "Chat Canvas":
    render_chat_view()
elif nav_view == "Deliverables":
    render_deliverables_view()
elif nav_view == "Knowledge Base":
    render_knowledge_base_view()
elif nav_view == "Models":
    render_models_view(models_list)
elif nav_view == "Air-Gap Audit":
    render_audit_view(net_status)
