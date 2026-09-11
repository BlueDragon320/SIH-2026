"""
Design System, Themes, and Custom CSS Injection for Air-Gapped Workbench UI.
"""
import streamlit as st

def get_theme_vars(is_dark: bool) -> str:
    if is_dark:
        return """
        :root {
            --bg-canvas: #131316;
            --bg-sidebar: #0e0f11;
            --bg-header: #18191d;
            --bg-card: #18191d;
            --bg-card-hover: #222328;
            --bg-input: #1c1d22;
            --border-color: rgba(255, 255, 255, 0.08);
            --border-hover: rgba(255, 255, 255, 0.18);
            --border-focus: #38bdf8;
            --text-primary: #f4f4f5;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --status-green: #10b981;
            --btn-primary-bg: #202126;
            --btn-primary-fg: #f4f4f5;
            --btn-primary-border: rgba(255, 255, 255, 0.12);
            --btn-primary-hover-bg: #282930;
            --btn-primary-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            --history-hover-bg: rgba(255, 255, 255, 0.05);
            --history-active-bg: rgba(255, 255, 255, 0.09);
            --history-active-border: rgba(255, 255, 255, 0.15);
            --diamond-border: rgba(255, 255, 255, 0.25);
            --diamond-active-border: #f59e0b;
            --diamond-active-bg: rgba(245, 158, 11, 0.15);
            --theme-toggle-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23f59e0b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='4'/%3E%3Cpath d='M12 2v2'/%3E%3Cpath d='M12 20v2'/%3E%3Cpath d='m4.93 4.93 1.41 1.41'/%3E%3Cpath d='m17.66 17.66 1.41 1.41'/%3E%3Cpath d='M2 12h2'/%3E%3Cpath d='M20 12h2'/%3E%3Cpath d='m6.34 17.66-1.41 1.41'/%3E%3Cpath d='m19.07 4.93-1.41 1.41'/%3E%3C/svg%3E");
        }
        """
    else:
        return """
        :root {
            --bg-canvas: #f8fafc;
            --bg-sidebar: #f1f5f9;
            --bg-header: #ffffff;
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --bg-input: #ffffff;
            --border-color: #e2e8f0;
            --border-hover: #cbd5e1;
            --border-focus: #3b82f6;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --accent-amber: #d97706;
            --accent-blue: #0284c7;
            --status-green: #059669;
            --btn-primary-bg: #ffffff;
            --btn-primary-fg: #0f172a;
            --btn-primary-border: #cbd5e1;
            --btn-primary-hover-bg: #f8fafc;
            --btn-primary-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
            --history-hover-bg: rgba(0, 0, 0, 0.04);
            --history-active-bg: #e2e8f0;
            --history-active-border: #cbd5e1;
            --diamond-border: rgba(0, 0, 0, 0.25);
            --diamond-active-border: #0f172a;
            --diamond-active-bg: rgba(0, 0, 0, 0.1);
            --theme-toggle-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%230f172a' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z'/%3E%3C/svg%3E");
        }
        """

def inject_global_css(is_dark: bool):
    theme_vars = get_theme_vars(is_dark)
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
        
        {theme_vars}

        [data-testid="stAppViewContainer"] {{
            background: var(--bg-canvas) !important;
        }}
        .stMain .block-container {{
            position: relative;
            max-width: 920px !important;
            padding-top: 1.25rem !important;
            padding-bottom: 6rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }}

        /* Reset Chrome Headers */
        header[data-testid="stHeader"] {{
            background: transparent !important;
            pointer-events: none !important;
            height: 0 !important;
            min-height: 0 !important;
            border: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }}
        [data-testid="stHeaderActionElements"],
        [data-testid="stDecoration"],
        [data-testid="stStatusWidget"] {{
            display: none !important;
        }}

        /* Sidebar Toggle Controls */
        [data-testid="stExpandSidebarButton"],
        button[data-testid="stExpandSidebarButton"] {{
            display: inline-flex !important;
            visibility: visible !important;
            pointer-events: auto !important;
            position: fixed !important;
            top: 14px !important;
            left: 14px !important;
            z-index: 1000000 !important;
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            width: 32px !important;
            height: 32px !important;
            align-items: center !important;
            justify-content: center !important;
            cursor: pointer !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
            transition: all 0.15s ease !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
        }}

        /* Telemetry Badges */
        .badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 6px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
            font-weight: 500;
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-primary);
        }}
        .badge-blue {{
            border-color: rgba(56, 189, 248, 0.25);
            color: var(--accent-blue);
        }}
        .badge-amber {{
            border-color: rgba(255, 179, 71, 0.3);
            color: var(--accent-amber);
        }}
        .badge-green {{
            border-color: rgba(52, 211, 153, 0.3);
            color: var(--status-green);
        }}
        .live-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: var(--status-green);
            box-shadow: 0 0 6px var(--status-green);
            display: inline-block;
        }}

        @keyframes pulse {{
            0% {{ opacity: 0.4; }}
            50% {{ opacity: 1.0; }}
            100% {{ opacity: 0.4; }}
        }}

        /* Left-Aligned Floating Chat Bar with Hover Glow */
        div[data-testid="stBottom"] {{
            background: transparent !important;
            background-color: transparent !important;
            border-top: none !important;
            padding: 0 0 16px 0 !important;
        }}
        div[data-testid="stBottom"] > div {{
            background: transparent !important;
            background-color: transparent !important;
            max-width: 840px !important;
            margin: 0 auto !important;
        }}
        div[data-testid="stChatInput"] {{
            max-width: 840px !important;
            margin: 0 auto !important;
            border-radius: 24px !important;
            background: #1c1d22 !important;
            background-color: #1c1d22 !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
            padding: 4px 14px !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}
        div[data-testid="stChatInput"]:hover {{
            border-color: rgba(255, 255, 255, 0.28) !important;
            box-shadow: 0 10px 36px rgba(0, 0, 0, 0.5) !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stChatInput"]:focus-within {{
            border-color: #38bdf8 !important;
            box-shadow: 0 0 14px rgba(56, 189, 248, 0.35) !important;
        }}
        div[data-testid="stChatInput"] textarea {{
            background: transparent !important;
            border: none !important;
            color: #f4f4f5 !important;
            font-size: 0.94rem !important;
            text-align: left !important;
            padding: 8px 4px !important;
        }}
        div[data-testid="stChatInput"] p {{
            text-align: left !important;
        }}
        div[data-testid="stChatInput"] button {{
            border-radius: 50% !important;
            background: #38bdf8 !important;
            color: #0f172a !important;
            border: none !important;
            transition: all 0.15s ease !important;
        }}
        div[data-testid="stChatInput"] button:hover {{
            transform: scale(1.1) !important;
            background: #0284c7 !important;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.5) !important;
        }}

        /* Disclaimer Footer */
        .disclaimer {{
            text-align: center;
            font-size: 0.74rem;
            color: var(--text-muted);
            margin-top: 0.85rem;
        }}
    </style>
    """, unsafe_allow_html=True)
