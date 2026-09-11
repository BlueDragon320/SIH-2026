"""
Air-Gap Audit View: Live hardware egress telemetry and tamper-evident audit logs.
"""
import streamlit as st
import pandas as pd
from frontend.api import api_get
from frontend.components import render_html

def render_audit_view(net_status: dict):
    render_html("""
    <div class="section-header">
        <h2>Air-Gap Verification & Audit</h2>
        <p>Live hardware egress telemetry proving 100% on-premises isolation.</p>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Network Telemetry")
        m1, m2 = st.columns(2)
        m1.metric("External Egress", f"{net_status.get('external_egress_rate_bps', 0.0)} B/s")
        m2.metric("External Ingress", f"{net_status.get('external_ingress_rate_bps', 0.0)} B/s")

        st.markdown("##### Monitored Interfaces")
        st.dataframe(pd.DataFrame(net_status.get("interfaces", [])), use_container_width=True, hide_index=True)

        st.caption("Live tcpdump command for judges:")
        st.code("sudo tcpdump -i any not host 127.0.0.1 -n -c 20", language="bash")

    with col2:
        st.markdown("##### Immutable Audit Records")
        logs = api_get("/v1/audit/logs") or []
        if logs:
            df_logs = pd.DataFrame(logs)[["timestamp", "task_id", "event_type", "model_used", "duration_ms"]]
            st.dataframe(df_logs, use_container_width=True, hide_index=True)
        else:
            st.caption("No audit events recorded.")
