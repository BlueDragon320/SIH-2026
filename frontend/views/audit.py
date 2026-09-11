"""
Air-Gap Audit View: Live hardware egress telemetry and tamper-evident audit logs.
Red Noir Design System with Crimson Accents.
"""
import streamlit as st
import pandas as pd
from frontend.api import api_get
from frontend.components import render_html

def render_audit_view(net_status: dict):
    render_html("""
    <div class="section-header">
        <h2>Air-Gap Verification & <span class="text-red">Audit</span></h2>
        <p>Live hardware egress telemetry proving 100% on-premises isolation.</p>
    </div>
    """)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        render_html('<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-bottom:10px;">NETWORK TELEMETRY</div>')
        m1, m2 = st.columns(2)
        m1.metric("External Egress", f"{net_status.get('external_egress_rate_bps', 0.0)} B/s")
        m2.metric("External Ingress", f"{net_status.get('external_ingress_rate_bps', 0.0)} B/s")

        st.markdown("<div style='margin: 1.25rem 0 0.75rem 0;'></div>", unsafe_allow_html=True)
        render_html('<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-bottom:10px;">MONITORED INTERFACES</div>')
        st.dataframe(pd.DataFrame(net_status.get("interfaces", [])), use_container_width=True, hide_index=True)

        st.caption("Live tcpdump command for verification:")
        st.code("sudo tcpdump -i any not host 127.0.0.1 -n -c 20", language="bash")

    with col2:
        render_html('<div style="font-family:\'JetBrains Mono\',monospace; font-size:0.74rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-muted); margin-bottom:10px;">IMMUTABLE AUDIT RECORDS</div>')
        logs = api_get("/v1/audit/logs") or []
        if logs:
            df_logs = pd.DataFrame(logs)[["timestamp", "task_id", "event_type", "model_used", "duration_ms"]]
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.caption("No audit events recorded.")
