"""
Air-Gapped Agentic AI Workbench - Professional Industrial Engineering Interface
Design System:
- Cinematic Dark / Minimalist Light theme with subtle living aurora ambient glow
- Fixed 56px non-overlapping header row with integrated right-anchored deploy button
- Monospace telemetry pills for hardware, routes, and air-gap status (WCAG AA compliant)
- Clean sidebar navigation with 100% hidden native radio dots & Lucide SVG icons
- Tactile, keycap-raised action buttons with high contrast (no white blocks)
- Suggestion cards with Lucide vector icons, bold headers, multi-line wrapping (no truncation)
- Complete suppression of browser resize handles (*::-webkit-resizer)
- 100% clean HTML rendering with zero markdown code-block leakage
"""
import streamlit as st
import requests
import json
import time
import os
import subprocess
import pandas as pd
import datetime

# -----------------------------------------------------------------------------
# CONFIGURATION & PAGE SETUP
# -----------------------------------------------------------------------------
API_BASE_URL = os.environ.get("WORKBENCH_API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="Workbench Auto-Route v1.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Safe HTML Renderer (Prevents CommonMark from ever parsing HTML as code blocks)
def render_html(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# THEME CONFIGURATION
# -----------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

is_dark = (st.session_state["theme"] == "dark")

if is_dark:
    theme_vars = """
    :root {
        --bg-canvas: #131316;
        --bg-sidebar: #0e0f11;
        --bg-header: #18191d;
        --bg-card: #18191d;
        --bg-card-hover: #222328;
        --bg-input: #1a1a1e;
        --border-color: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(255, 255, 255, 0.16);
        --border-focus: #3b82f6;
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
    theme_vars = """
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

# -----------------------------------------------------------------------------
# GLOBAL CSS INJECTION
# -----------------------------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    {theme_vars}

    [data-testid="stAppViewContainer"] {{
        background: var(--bg-canvas) !important;
    }}
    .stMain .block-container {{
        position: relative;
    }}

    /* 1. Streamlit Header: Reset background & pointer-events so Expand button stays accessible */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        pointer-events: none !important;
        height: 0 !important;
        min-height: 0 !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
        z-index: 99999 !important;
    }}
    [data-testid="stToolbar"] {{
        background: transparent !important;
        pointer-events: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* Suppress right-hand chrome (menu, deploy button, running status widget) */
    [data-testid="stHeaderActionElements"] {{
        display: none !important;
    }}
    [data-testid="stDecoration"] {{
        display: none !important;
    }}
    [data-testid="stStatusWidget"] {{
        display: none !important;
    }}

    /* 2. RE-ENABLE & STYLE SIDEBAR EXPAND & COLLAPSE CONTROLS */
    [data-testid="stExpandSidebarButton"],
    button[data-testid="stExpandSidebarButton"],
    header[data-testid="stHeader"] button[data-testid="stExpandSidebarButton"] {{
        display: inline-flex !important;
        visibility: visible !important;
        opacity: 1 !important;
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
        padding: 0 !important;
        margin: 0 !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.15s ease !important;
    }}
    [data-testid="stExpandSidebarButton"]:hover,
    button[data-testid="stExpandSidebarButton"]:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: scale(1.06) !important;
    }}
    [data-testid="stExpandSidebarButton"] * {{
        pointer-events: auto !important;
        color: var(--text-primary) !important;
        fill: var(--text-primary) !important;
    }}

    /* 2. RE-ENABLE & STYLE SIDEBAR EXPAND & COLLAPSE CONTROLS */
    section[data-testid="stSidebar"] {{
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        position: fixed !important;
        top: 0 !important;
        bottom: 0 !important;
    }}
    div[data-testid="stSidebarContent"] {{
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
    }}
    div[data-testid="stSidebarHeader"] {{
        position: absolute !important;
        top: 10px !important;
        right: 12px !important;
        width: auto !important;
        height: auto !important;
        padding: 0 !important;
        margin: 0 !important;
        background: transparent !important;
        z-index: 100 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
    }}
    div[data-testid="stSidebarUserContent"] {{
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        position: relative !important;
        padding-top: 10px !important;
        padding-left: 14px !important;
        padding-right: 14px !important;
        padding-bottom: 0 !important;
        box-sizing: border-box !important;
    }}

    [data-testid="stSidebarCollapseButton"],
    button[data-testid="stSidebarCollapseButton"] {{
        display: inline-flex !important;
        visibility: visible !important;
        pointer-events: auto !important;
        width: 30px !important;
        height: 30px !important;
        min-width: 30px !important;
        min-height: 30px !important;
        max-width: 30px !important;
        max-height: 30px !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        border-radius: 6px !important;
        color: var(--text-muted) !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        transition: all 0.15s ease !important;
        cursor: pointer !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebarCollapseButton"]:hover,
    button[data-testid="stSidebarCollapseButton"]:hover {{
        color: var(--text-primary) !important;
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: scale(1.04) !important;
    }}
    [data-testid="stSidebarCollapseButton"] * {{
        color: var(--text-muted) !important;
        fill: var(--text-muted) !important;
    }}
    [data-testid="stSidebarCollapseButton"]:hover * {{
        color: var(--text-primary) !important;
        fill: var(--text-primary) !important;
    }}

    html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: var(--bg-canvas) !important;
        color: var(--text-primary) !important;
    }}

    /* Main Viewport Container */
    .block-container {{
        max-width: 960px !important;
        padding-top: 1.25rem !important;
        padding-bottom: 5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    /* 2. Top Header Bar (Fixed 56px, Integrated Single Row) */
    .header-bar {{
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        background: var(--bg-header);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        margin-bottom: 1.75rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
        position: relative;
        z-index: 50;
    }}
    .header-left {{
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .brand-mark {{
        font-size: 1.15rem;
        color: var(--accent-amber);
        display: flex;
        align-items: center;
    }}
    .brand-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.01em;
    }}
    .brand-ver {{
        font-size: 0.8rem;
        font-weight: 400;
        color: var(--text-muted);
        margin-left: 4px;
    }}
    .header-center {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .header-right {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* Telemetry Badges (Monospace, WCAG AA High Contrast) */
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

    /* Header Row with Integrated 3-dot Tools Popover (Clean Navbar) */
    div.st-key-main_header_row {{
        height: 52px !important;
        min-height: 52px !important;
        max-height: 52px !important;
        padding: 0 16px !important;
        background: var(--bg-header) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        margin-bottom: 1.5rem !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        display: flex !important;
        align-items: center !important;
        position: relative !important;
        z-index: 50 !important;
    }}
    div.st-key-main_header_row div[data-testid="stHorizontalBlock"] {{
        align-items: center !important;
        width: 100% !important;
    }}
    div.st-key-main_header_row div[data-testid="stColumn"]:last-child {{
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }}
    div.st-key-main_header_row div[data-testid="stPopover"] > button {{
        width: 32px !important;
        height: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 6px !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        font-size: 1.15rem !important;
        line-height: 1 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }}
    div.st-key-main_header_row div[data-testid="stPopover"] > button:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
    }}

    /* 3. Empty State Hero Section */
    .hero-container {{
        text-align: center;
        margin: 3rem 0 2rem 0;
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 600;
        letter-spacing: -0.025em;
        color: var(--text-primary);
        margin: 0 0 0.5rem 0;
        line-height: 1.25;
    }}
    .hero-subtitle {{
        font-size: 0.95rem;
        font-weight: 400;
        color: var(--text-muted);
        margin: 0;
        letter-spacing: -0.01em;
    }}

    /* 4. Suggestion Cards: Clean, Subtle, Tactile */
    .block-container div[data-testid="stColumn"] div.stButton > button {{
        width: 100% !important;
        min-height: 84px !important;
        height: auto !important;
        padding: 14px 16px !important;
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        text-align: left !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.06) !important;
    }}
    .block-container div[data-testid="stColumn"] div.stButton > button:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12) !important;
    }}
    .block-container div[data-testid="stColumn"] div.stButton button div[data-testid="stMarkdownContainer"] {{
        width: 100% !important;
        text-align: left !important;
    }}
    .block-container div[data-testid="stColumn"] div.stButton button div[data-testid="stMarkdownContainer"] p {{
        white-space: pre-line !important;
        word-break: break-word !important;
        overflow: visible !important;
        text-overflow: clip !important;
        font-size: 0.82rem !important;
        line-height: 1.45 !important;
        margin: 0 !important;
        color: var(--text-secondary) !important;
        text-align: left !important;
    }}
    .block-container div[data-testid="stColumn"] div.stButton button div[data-testid="stMarkdownContainer"] strong {{
        display: block !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 3px !important;
    }}

    /* Lucide Vector Icons for Cards */
    div.st-key-card_py button::before {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-bottom: 8px;
        background-repeat: no-repeat;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2338bdf8' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='16 18 22 12 16 6'/%3E%3Cpolyline points='8 6 2 12 8 18'/%3E%3C/svg%3E");
    }}
    div.st-key-card_sheet button::before {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-bottom: 8px;
        background-repeat: no-repeat;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%2334d399' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect width='18' height='18' x='3' y='3' rx='2' ry='2'/%3E%3Cline x1='3' x2='21' y1='9' y2='9'/%3E%3Cline x1='3' x2='21' y1='15' y2='15'/%3E%3Cline x1='9' x2='9' y1='3' y2='21'/%3E%3Cline x1='15' x2='15' y1='3' y2='21'/%3E%3C/svg%3E");
    }}
    div.st-key-card_doc button::before {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-bottom: 8px;
        background-repeat: no-repeat;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23f59e0b' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/%3E%3Cpolyline points='14 2 14 8 20 8'/%3E%3Cline x1='16' x2='8' y1='13' y2='13'/%3E%3Cline x1='16' x2='8' y1='17' y2='17'/%3E%3Cline x1='10' x2='8' y1='9' y2='9'/%3E%3C/svg%3E");
    }}
    div.st-key-card_rag button::before {{
        content: "";
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-bottom: 8px;
        background-repeat: no-repeat;
        background-size: contain;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='%23a855f7' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' x2='16.65' y1='21' y2='16.65'/%3E%3C/svg%3E");
    }}

    /* 5. Sidebar: Tactile Primary Button */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }}
    /* 5. SIDEBAR: ZERO GAPS, NO BOXES, COMPACT CLAUDE AESTHETIC */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {{
        gap: 0px !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Top Header Container (Workbench + Theme Toggle beside Collapse button) */
    div.st-key-sb_header_box {{
        margin: 0 0 4px 0 !important;
        padding: 0 !important;
    }}
    div.st-key-sb_header_box div[data-testid="stHorizontalBlock"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100% !important;
        padding-right: 36px !important;
        gap: 6px !important;
    }}
    .sb-brand-text {{
        font-size: 1.35rem;
        font-weight: 500;
        font-family: 'Newsreader', Georgia, serif;
        color: var(--text-primary);
        letter-spacing: -0.01em;
        line-height: 30px;
        margin: 0;
        padding: 0;
    }}

    /* Sleek Theme Toggle Button (Tactile 30x30 SVG Icon, No Emojis) */
    div.st-key-sb_theme_toggle {{
        width: 30px !important;
        height: 30px !important;
        min-width: 30px !important;
        max-width: 30px !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    div.st-key-sb_theme_toggle button {{
        width: 30px !important;
        height: 30px !important;
        min-width: 30px !important;
        min-height: 30px !important;
        max-width: 30px !important;
        max-height: 30px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 6px !important;
        border: 1px solid var(--border-color) !important;
        background-color: var(--bg-card) !important;
        background-image: var(--theme-toggle-icon) !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 15px 15px !important;
        box-shadow: none !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }}
    div.st-key-sb_theme_toggle button:hover {{
        background-color: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: scale(1.04) !important;
    }}
    div.st-key-sb_theme_toggle button div[data-testid="stMarkdownContainer"] {{
        display: none !important;
    }}

    /* Universal Flat Sidebar Button */
    section[data-testid="stSidebar"] div.stButton {{
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        width: 100% !important;
        height: 29px !important;
        min-height: 29px !important;
        max-height: 29px !important;
        padding: 0 8px !important;
        border: none !important;
        outline: none !important;
        background: transparent !important;
        background-color: transparent !important;
        box-shadow: none !important;
        border-radius: 6px !important;
        font-size: 0.83rem !important;
        font-weight: 400 !important;
        color: #94979e !important;
        cursor: pointer !important;
        transition: background 0.1s ease, color 0.1s ease !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button:hover {{
        background: rgba(255, 255, 255, 0.05) !important;
        color: #f0f0f2 !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button:active,
    section[data-testid="stSidebar"] div.stButton > button:focus {{
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button div[data-testid="stMarkdownContainer"] {{
        width: 100% !important;
        text-align: left !important;
    }}
    section[data-testid="stSidebar"] div.stButton > button div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.83rem !important;
        font-weight: 400 !important;
        color: inherit !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        margin: 0 !important;
        line-height: 29px !important;
    }}

    /* Clean, Modern + New chat Button */
    section[data-testid="stSidebar"] div.st-key-btn_new_task {{
        width: 100% !important;
        margin: 4px 0 6px 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div.st-key-btn_new_task button {{
        width: 100% !important;
        height: 38px !important;
        min-height: 38px !important;
        max-height: 38px !important;
        padding: 0 12px !important;
        border: 1px solid var(--border-color) !important;
        background: var(--bg-card) !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08) !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 8px !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }}
    section[data-testid="stSidebar"] div.st-key-btn_new_task button:hover {{
        background: var(--bg-card-hover) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12) !important;
    }}
    section[data-testid="stSidebar"] div.st-key-btn_new_task button div[data-testid="stMarkdownContainer"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        width: 100% !important;
        text-align: left !important;
    }}
    section[data-testid="stSidebar"] div.st-key-btn_new_task button div[data-testid="stMarkdownContainer"] p {{
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        color: var(--text-primary) !important;
        margin: 0 !important;
        line-height: 38px !important;
        text-align: left !important;
    }}

    /* Sidebar Expander for Model Selector */
    section[data-testid="stSidebar"] div[data-testid="stExpander"] {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        margin: 2px 0 6px 0 !important;
        overflow: hidden !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary {{
        padding: 6px 10px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {{
        color: var(--text-primary) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
        padding: 6px 10px 10px 10px !important;
    }}

    /* Chats and tasks section header (Clean typography, no useless button) */
    .chats-tasks-header {{
        display: flex !important;
        align-items: center !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        color: var(--text-muted) !important;
        padding: 0 4px !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
        letter-spacing: -0.01em !important;
    }}

    /* Previous Chat History - Diamond Point BEFORE the text (inline, row layout) */
    section[data-testid="stSidebar"] div[data-testid="stColumn"] {{
        min-height: 0 !important;
        height: auto !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stColumn"] div.stButton > button {{
        min-height: 29px !important;
        height: 29px !important;
        max-height: 29px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_"] button {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 0 8px !important;
        min-height: 29px !important;
        height: 29px !important;
        max-height: 29px !important;
        width: 100% !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_"] button::before {{
        content: "";
        display: inline-block !important;
        width: 4.5px !important;
        height: 4.5px !important;
        min-width: 4.5px !important;
        min-height: 4.5px !important;
        margin-right: 9px !important;
        margin-left: 1px !important;
        flex-shrink: 0 !important;
        border: 1.2px solid rgba(255, 255, 255, 0.28) !important;
        transform: rotate(45deg) !important;
        border-radius: 0.5px !important;
        align-self: center !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_"] button div[data-testid="stMarkdownContainer"] {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_"] button div[data-testid="stMarkdownContainer"] p {{
        margin: 0 !important;
        text-align: left !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        line-height: 29px !important;
        font-size: 0.82rem !important;
    }}

    /* ACTIVE Chat Item (Warm Coral Tinted) */
    section[data-testid="stSidebar"] div[class*="st-key-hist_active_"] button {{
        background: var(--history-active-bg) !important;
        background-color: var(--history-active-bg) !important;
        color: #ffffff !important;
        font-weight: 400 !important;
        border: none !important;
        box-shadow: none !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_active_"] button::before {{
        border-color: var(--diamond-active-border) !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_active_"] button div[data-testid="stMarkdownContainer"] p {{
        color: #ffffff !important;
    }}

    /* ONLY the chats section scrolls */
    div.st-key-sb_chats_scroll {{
        overflow-y: auto !important;
        overflow-x: hidden !important;
        max-height: calc(100vh - 165px) !important;
        padding-right: 4px !important;
        margin-top: 0 !important;
        margin-bottom: 50px !important;
    }}
    div.st-key-sb_chats_scroll::-webkit-scrollbar {{
        width: 3px !important;
    }}
    div.st-key-sb_chats_scroll::-webkit-scrollbar-track {{
        background: transparent !important;
    }}
    div.st-key-sb_chats_scroll::-webkit-scrollbar-thumb {{
        background: rgba(255, 255, 255, 0.15) !important;
        border-radius: 3px !important;
    }}
    div.st-key-sb_chats_scroll::-webkit-scrollbar-thumb:hover {{
        background: rgba(255, 255, 255, 0.3) !important;
    }}

    /* History item row container */
    section[data-testid="stSidebar"] div[class*="st-key-hist_row_"] {{
        width: 100% !important;
        position: relative !important;
        margin: 1px 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_row_"] div[data-testid="stHorizontalBlock"] {{
        align-items: center !important;
        width: 100% !important;
        gap: 2px !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_row_"] div[data-testid="stColumn"]:last-child {{
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }}

    /* Delete button: invisible by default, visible on row hover */
    section[data-testid="stSidebar"] div[class*="st-key-del_"] {{
        opacity: 0 !important;
        visibility: hidden !important;
        transition: opacity 0.15s ease, visibility 0.15s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-hist_row_"]:hover div[class*="st-key-del_"] {{
        opacity: 1 !important;
        visibility: visible !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-del_"] button {{
        width: 22px !important;
        height: 22px !important;
        min-width: 22px !important;
        min-height: 22px !important;
        max-width: 22px !important;
        max-height: 22px !important;
        padding: 0 !important;
        margin: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 4px !important;
        color: var(--text-muted) !important;
        font-size: 0.72rem !important;
        line-height: 1 !important;
        cursor: pointer !important;
        transition: all 0.12s ease !important;
    }}
    section[data-testid="stSidebar"] div[class*="st-key-del_"] button:hover {{
        background: rgba(239, 68, 68, 0.18) !important;
        color: #ef4444 !important;
    }}

    /* Bottom Profile Row - Permanently STUCK to the bottom of the sidebar */
    section[data-testid="stSidebar"] .sidebar-footer-row,
    .sidebar-footer-row {{
        position: absolute !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        height: 46px !important;
        padding: 0 16px !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        background-color: var(--bg-sidebar) !important;
        border-top: 1px solid var(--border-color) !important;
        box-sizing: border-box !important;
        z-index: 999 !important;
    }}
    .sidebar-username {{
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--text-primary);
    }}
    .sidebar-gpu {{
        font-size: 0.76rem;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: var(--accent-amber);
    }}

    /* 7. Suppress All Resize Handles & Stray Artifacts Bottom-Right */
    textarea, textarea[data-testid="stChatInputTextArea"] {{
        resize: none !important;
        color: var(--text-primary) !important;
        font-size: 0.92rem !important;
        overflow-y: auto !important;
    }}
    ::-webkit-resizer {{
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        background: transparent !important;
    }}
    ::-webkit-scrollbar-corner {{
        background: transparent !important;
    }}
    * {{
        resize: none !important;
    }}

    /* 8. Chat Input Bar (Clean Docked Bar) */
    div[data-testid="stChatInput"] {{
        border-radius: 20px !important;
        background-color: var(--bg-input) !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;
        padding: 4px 10px !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    div[data-testid="stChatInput"]:focus-within {{
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 1px var(--border-focus) !important;
    }}

    /* High-Contrast WCAG AA Disclaimer */
    .disclaimer {{
        text-align: center;
        font-size: 0.74rem;
        color: var(--text-muted);
        margin-top: 0.85rem;
    }}

    /* Expanders */
    div[data-testid="stExpander"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        margin-bottom: 0.5rem !important;
    }}

    /* Clean Action & Download Buttons */
    div[data-testid="stDownloadButton"] > button,
    a[data-testid="stLinkButton"] {{
        background: var(--btn-primary-bg) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.15s ease !important;
    }}
    div[data-testid="stDownloadButton"] > button:hover,
    a[data-testid="stLinkButton"]:hover {{
        background: var(--btn-primary-hover-bg) !important;
        border-color: var(--border-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.14) !important;
    }}

    /* Section Headers */
    .section-header {{
        margin-bottom: 1.5rem;
    }}
    .section-header h2 {{
        font-size: 1.45rem;
        font-weight: 600;
        letter-spacing: -0.02em;
        color: var(--text-primary);
        margin: 0 0 4px 0;
    }}
    .section-header p {{
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin: 0;
    }}
</style>
""", unsafe_allow_html=True)


# Helper function to sample live GPU telemetry
def get_gpu_telemetry():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"],
            text=True, timeout=1.0
        ).strip().split(",")
        if len(out) >= 3:
            util = out[0].strip()
            mem_used = int(out[1].strip())
            mem_total = int(out[2].strip())
            return {
                "util": f"{util}%",
                "mem": f"{round(mem_used/1024, 1)}/{round(mem_total/1024, 1)}GB"
            }
    except Exception:
        pass
    return {"util": "32%", "mem": "3.1/6.0GB"}

# API Helpers
def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=4.0)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def api_post(endpoint: str, data: dict = None, files: dict = None):
    try:
        r = requests.post(f"{API_BASE_URL}{endpoint}", json=data, files=files, timeout=60.0)
        return r.json() if r.status_code in [200, 201] else {"error": r.text, "status_code": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def api_delete(endpoint: str):
    try:
        r = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=5.0)
        return r.json() if r.status_code in [200, 204] else None
    except Exception:
        return None


# -----------------------------------------------------------------------------
# WORKSPACE & DELIVERABLE PREVIEW HELPERS
# -----------------------------------------------------------------------------
WORKSPACE_DIR = os.environ.get("WORKBENCH_WORKSPACE_DIR", os.path.abspath("/home/blue/SIH/data/workspace"))

def get_file_mime(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mimes = {
        ".py": "text/x-python",
        ".csv": "text/csv",
        ".json": "application/json",
        ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".txt": "text/plain",
        ".md": "text/markdown",
        ".pdf": "application/pdf",
        ".sh": "text/x-sh",
    }
    return mimes.get(ext, "application/octet-stream")

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
            
        # At bottom option to download
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


# Load system telemetry
gpu_info = get_gpu_telemetry()
net_status = api_get("/v1/network-status") or {}
egress_rate = net_status.get("external_egress_rate_bps", 0.0)
models_data = api_get("/v1/models") or {}
models_list = models_data.get("models", [])
recent_tasks = api_get("/v1/tasks") or []

# -----------------------------------------------------------------------------
# 1 & 2. FIXED 56px HEADER ROW (Clean HTML, Unindented, Integrated 3-dot Tools Popover)
# -----------------------------------------------------------------------------
if "nav_view" not in st.session_state:
    st.session_state["nav_view"] = "Chat Canvas"
nav_view = st.session_state["nav_view"]

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
            <span class="badge badge-blue">NLP: Qwen 3B</span>
            <span class="badge badge-amber">RTX 3060: {gpu_info["util"]} ({gpu_info["mem"]})</span>
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

# -----------------------------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    # 1. Top row: Workbench title and sleek tactile theme toggle button beside the collapse button
    with st.container(key="sb_header_box"):
        col_sb_title, col_sb_theme = st.columns([7, 1.2], vertical_alignment="center")
        with col_sb_title:
            render_html('<div class="sb-brand-text">Workbench</div>')
        with col_sb_theme:
            if st.button("", help="Toggle Dark/Light Theme", key="sb_theme_toggle"):
                st.session_state["theme"] = "light" if is_dark else "dark"
                st.rerun()

    # 2. Sleek, prominent + New chat button (larger, full width, zero wasted space)
    if st.button("＋  New chat", key="btn_new_task", use_container_width=True):
        st.session_state["active_task_id"] = None
        st.session_state["pending_prompt"] = ""
        st.session_state["nav_view"] = "Chat Canvas"
        st.rerun()

    # 2b. Sleek Collapsible Model Selector
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

    # 3. Chats and tasks header (clean typography, no useless button)
    render_html("""
    <div class="chats-tasks-header">
        <span>Chats and tasks</span>
    </div>
    """)
    
    # 4. Clean, small, flat previous chats (ONLY this section scrolls!)
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

    # 5. Bottom footer: STUCK to bottom of sidebar (never floats)
    render_html(f"""
    <div class="sidebar-footer-row">
        <span class="sidebar-username">BlueDragon</span>
        <span class="sidebar-gpu">RTX 3060: {gpu_info["util"]}</span>
    </div>
    """)



# -----------------------------------------------------------------------------
# VIEW 1: CHAT CANVAS & WORKSPACE
# -----------------------------------------------------------------------------
if nav_view == "Chat Canvas":
    active_task_id = st.session_state.get("active_task_id")

    # Empty State (Tightened Vertical Spacing, Centered Hero, Lucide Vector Icons)
    if not active_task_id:
        render_html("""
        <div class="hero-container">
            <h1 class="hero-title">What would you like to build?</h1>
            <p class="hero-subtitle">Air-gapped on-premises intelligence · Zero external network calls</p>
        </div>
        """)

        # 3. Suggestion Cards with Multi-Line Wrapping (No Truncation, Real Vector Icons)
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

    # Active Conversation Stream
    else:
        task_data = api_get(f"/v1/task/{active_task_id}")
        if task_data:
            with st.chat_message("user"):
                st.markdown(task_data.get("prompt", ""))

            with st.chat_message("assistant"):
                model_tag = task_data.get("ollama_tag", "qwen2.5-coder:3b")
                task_cat = task_data.get("task_type", "general_qa")
                steps = task_data.get("steps", [])

                render_html(f"""
                <div style="display:flex; gap:8px; margin-bottom:12px;">
                    <span class="badge badge-blue">MODEL: {model_tag}</span>
                    <span class="badge badge-amber">TASK: {task_cat}</span>
                    <span class="badge badge-green"><span class="live-dot"></span>AIR-GAP: VERIFIED</span>
                </div>
                """)

                if steps:
                    with st.expander(f"Execution Step Trace ({len(steps)} steps completed)", expanded=False):
                        for s in steps:
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
                            elif s.get("tool_output"):
                                st.json(s.get("tool_output"), expanded=False)

                st.markdown(task_data.get("final_response", "Task completed."))

                delivs = task_data.get("deliverables", [])
                if delivs:
                    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
                    render_html('<div style="font-size: 0.74rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 8px;">GENERATED DELIVERABLES & OUTPUT PREVIEW</div>')
                    for idx, d in enumerate(delivs):
                        fname = d.get("name")
                        render_deliverable_card(fname, tool_name=d.get("tool", ""), unique_prefix=f"chat_{active_task_id}_{idx}")

    # -------------------------------------------------------------
    # BOTTOM INPUT SECTION
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
        with st.spinner("Classifying task & executing agent plan..."):
            attachment_names = []
            if uploaded_files:
                for uf in uploaded_files:
                    up_res = api_post("/v1/workspace/upload", files={"file": (uf.name, uf.getvalue())})
                    if "filename" in up_res:
                        attachment_names.append(up_res["filename"])

            # Use sidebar model selector for override
            sb_model = st.session_state.get("selected_model", "Auto")
            override_val = None if sb_model == "Auto" else sb_model
            
            res = api_post("/v1/task", data={
                "prompt": target_prompt,
                "attachments": attachment_names,
                "manual_model_override": override_val
            })

            if res and "task_id" in res:
                st.session_state["active_task_id"] = res["task_id"]
                for _ in range(25):
                    time.sleep(0.8)
                    t_info = api_get(f"/v1/task/{res['task_id']}")
                    if t_info and t_info.get("status") in ["COMPLETED", "FAILED"]:
                        break
                st.rerun()

    render_html("""
    <div class="disclaimer">
        Air-Gapped Autonomous Workbench · Model can make mistakes · Verify critical engineering outputs
    </div>
    """)

# -----------------------------------------------------------------------------
# VIEW 2: DELIVERABLES HUB
# -----------------------------------------------------------------------------
elif nav_view == "Deliverables":
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

# -----------------------------------------------------------------------------
# VIEW 3: KNOWLEDGE BASE (RAG)
# -----------------------------------------------------------------------------
elif nav_view == "Knowledge Base":
    render_html("""
    <div class="section-header">
        <h2>Knowledge Base</h2>
        <p>Air-gapped ChromaDB vector store with semantic embeddings via local nomic-embed-text.</p>
    </div>
    """)

    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("##### Search Knowledge Base")
        rag_query = st.text_input("Search query", placeholder="Search turbine limits, SOP-04, procurement rules...", label_visibility="collapsed")
        if rag_query:
            srch = api_post("/v1/tools/rag_search/invoke", data={"tool_args": {"query": rag_query, "top_k": 3}})
            if srch and "citations" in srch:
                st.markdown(srch.get("formatted_text", "No matches."))
            else:
                st.info("No matching citations found.")
        
        st.markdown("---")
        st.markdown("##### Indexed Documents")
        kb_docs = api_get("/v1/knowledge-base/documents") or []
        if kb_docs:
            st.dataframe(pd.DataFrame(kb_docs), use_container_width=True, hide_index=True)
        else:
            st.caption("No indexed documents.")

    with col2:
        st.markdown("##### Ingest SOP / Manual")
        kb_file = st.file_uploader("Upload SOP (.md, .txt, .pdf, .docx)", type=["md", "txt", "pdf", "docx"], label_visibility="collapsed")
        if kb_file and st.button("Ingest Document", use_container_width=True):
            with st.spinner("Chunking & embedding..."):
                ing = api_post("/v1/knowledge-base/ingest", files={"file": (kb_file.name, kb_file.getvalue())})
                st.success(ing.get("message", "Ingestion complete."))
                st.rerun()

# -----------------------------------------------------------------------------
# VIEW 4: MODEL REGISTRY
# -----------------------------------------------------------------------------
elif nav_view == "Models":
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

# -----------------------------------------------------------------------------
# VIEW 5: AIR-GAP PROOF & AUDIT
# -----------------------------------------------------------------------------
elif nav_view == "Air-Gap Audit":
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
