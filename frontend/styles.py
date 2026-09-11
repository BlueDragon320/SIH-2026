"""
Red Noir Design System for Air-Gapped Workbench UI.
Typography: Manrope (Headings & Hero), Inter (Body & Controls), JetBrains Mono (Badges, Code, Telemetry).
Colors: Deep Black Canvas (#000000), Dark Sidebar (#070709), Crimson Red (#ef233c), Crimson Glow rgba(239, 35, 60, 0.45).
Card Surfaces: rgba(24, 24, 27, 0.65) with border rgba(255, 255, 255, 0.09), hover #ef233c.
"""
import streamlit as st

def get_theme_vars(is_dark: bool) -> str:
    if is_dark:
        return """
        :root {
            --bg-canvas: #000000;
            --bg-sidebar: #070709;
            --bg-header: rgba(7, 7, 9, 0.85);
            --bg-card: rgba(24, 24, 27, 0.65);
            --bg-card-hover: rgba(39, 39, 42, 0.8);
            --bg-input: #0e0e11;
            --border-color: rgba(255, 255, 255, 0.09);
            --border-hover: rgba(255, 255, 255, 0.22);
            --border-focus: #ef233c;
            --text-primary: #f4f4f5;
            --text-secondary: #a1a1aa;
            --text-muted: #71717a;
            --accent-red: #ef233c;
            --accent-red-glow: rgba(239, 35, 60, 0.45);
            --accent-red-bg: rgba(239, 35, 60, 0.08);
            --accent-red-border: rgba(239, 35, 60, 0.4);
            --accent-amber: #f59e0b;
            --accent-blue: #38bdf8;
            --status-green: #10b981;
            --btn-primary-bg: #ef233c;
            --btn-primary-fg: #ffffff;
            --btn-primary-border: #ef233c;
            --btn-primary-hover-bg: #d90429;
            --btn-new-bg: rgba(24, 24, 27, 0.75);
            --btn-new-fg: #f4f4f5;
            --btn-new-border: #ef233c;
            --btn-new-hover-bg: rgba(239, 35, 60, 0.12);
            --btn-new-hover-border: #ef233c;
            --history-hover-bg: rgba(255, 255, 255, 0.05);
            --history-active-bg: rgba(239, 35, 60, 0.12);
            --history-active-border: #ef233c;
            --theme-toggle-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ef233c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='4'/%3E%3Cpath d='M12 2v2'/%3E%3Cpath d='M12 20v2'/%3E%3Cpath d='m4.93 4.93 1.41 1.41'/%3E%3Cpath d='m17.66 17.66 1.41 1.41'/%3E%3Cpath d='M2 12h2'/%3E%3Cpath d='M20 12h2'/%3E%3Cpath d='m6.34 17.66-1.41 1.41'/%3E%3Cpath d='m19.07 4.93-1.41 1.41'/%3E%3C/svg%3E");
        }
        """
    else:
        return """
        :root {
            --bg-canvas: #f8fafc;
            --bg-sidebar: #f1f5f9;
            --bg-header: rgba(255, 255, 255, 0.9);
            --bg-card: #ffffff;
            --bg-card-hover: #f1f5f9;
            --bg-input: #ffffff;
            --border-color: #e2e8f0;
            --border-hover: #cbd5e1;
            --border-focus: #ef233c;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-muted: #64748b;
            --accent-red: #ef233c;
            --accent-red-glow: rgba(239, 35, 60, 0.3);
            --accent-red-bg: rgba(239, 35, 60, 0.08);
            --accent-red-border: rgba(239, 35, 60, 0.35);
            --accent-amber: #d97706;
            --accent-blue: #0284c7;
            --status-green: #059669;
            --btn-primary-bg: #ef233c;
            --btn-primary-fg: #ffffff;
            --btn-primary-border: #ef233c;
            --btn-primary-hover-bg: #d90429;
            --btn-new-bg: #ffffff;
            --btn-new-fg: #0f172a;
            --btn-new-border: #ef233c;
            --btn-new-hover-bg: rgba(239, 35, 60, 0.08);
            --btn-new-hover-border: #ef233c;
            --history-hover-bg: rgba(0, 0, 0, 0.04);
            --history-active-bg: rgba(239, 35, 60, 0.08);
            --history-active-border: #ef233c;
            --theme-toggle-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23ef233c' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3a6 6 0 0 0 9 9 9 0 1 1-9-9Z'/%3E%3C/svg%3E");
        }
        """

def inject_global_css(is_dark: bool):
    theme_vars = get_theme_vars(is_dark)
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
        
        {theme_vars}

        /* 1. Red Selection Highlight */
        ::selection {{
            background: #ef233c !important;
            color: #ffffff !important;
        }}
        ::-moz-selection {{
            background: #ef233c !important;
            color: #ffffff !important;
        }}

        /* 2. Base Typography & Dark Grid Canvas with Vignette */
        html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: var(--bg-canvas) !important;
            color: var(--text-primary) !important;
            letter-spacing: -0.01em;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-canvas) !important;
            background-image: 
                radial-gradient(ellipse at 50% 0%, rgba(239, 35, 60, 0.09) 0%, transparent 65%),
                linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px) !important;
            background-size: 100% 100%, 40px 40px, 40px 40px !important;
            background-attachment: fixed !important;
        }}

        .stMain .block-container {{
            position: relative;
            max-width: 920px !important;
            padding-top: 1.25rem !important;
            padding-bottom: 6rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }}

        /* 3. Hide Native Streamlit Header Controls */
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

        /* 4. Sidebar Expand / Toggle Controls */
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
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4) !important;
            transition: all 0.2s ease !important;
        }}
        [data-testid="stExpandSidebarButton"]:hover {{
            border-color: #ef233c !important;
            box-shadow: 0 0 12px rgba(239, 35, 60, 0.4) !important;
        }}

        section[data-testid="stSidebar"] {{
            background-color: var(--bg-sidebar) !important;
            border-right: 1px solid var(--border-color) !important;
        }}

        /* Freeze sidebar container so only the chats list scrolls */
        section[data-testid="stSidebar"] > div:first-child,
        section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{
            overflow: hidden !important;
            display: flex !important;
            flex-direction: column !important;
            height: 100vh !important;
            max-height: 100vh !important;
            padding-top: 1rem !important;
            padding-bottom: 0.5rem !important;
        }}

        /* 5. Top Header Row Styling */
        div[data-testid="stVerticalBlock"]:has(> div[data-testid="stHorizontalBlock"] div.header-left) {{
            position: sticky !important;
            top: 0 !important;
            z-index: 9999 !important;
            background: var(--bg-header) !important;
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            padding: 8px 14px !important;
            margin-bottom: 2rem !important;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.45) !important;
        }}

        .brand-title {{
            font-family: 'Manrope', sans-serif !important;
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            display: inline-flex;
            align-items: center;
        }}
        .brand-ver {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 4px;
            background: rgba(239, 35, 60, 0.08);
            color: #ef233c;
            border: 1px solid rgba(239, 35, 60, 0.35);
            margin-left: 6px;
        }}

        /* 6. Crimson & Telemetry Badges */
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
            letter-spacing: 0.02em;
        }}
        .badge-red,
        .badge-lime {{
            border-color: rgba(239, 35, 60, 0.4) !important;
            color: #ef233c !important;
            background: rgba(239, 35, 60, 0.08) !important;
        }}
        .badge-blue {{
            border-color: rgba(56, 189, 248, 0.3) !important;
            color: var(--accent-blue) !important;
            background: rgba(56, 189, 248, 0.08) !important;
        }}
        .badge-amber {{
            border-color: rgba(245, 158, 11, 0.3) !important;
            color: var(--accent-amber) !important;
            background: rgba(245, 158, 11, 0.08) !important;
        }}
        .badge-green {{
            border-color: rgba(16, 185, 129, 0.3) !important;
            color: var(--status-green) !important;
            background: rgba(16, 185, 129, 0.08) !important;
        }}
        .badge-muted {{
            border-color: var(--border-color) !important;
            color: var(--text-muted) !important;
            background: var(--bg-card) !important;
        }}

        .live-dot {{
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #ef233c !important;
            box-shadow: 0 0 8px #ef233c !important;
            display: inline-block;
            animation: pulse-red 2s infinite;
        }}

        @keyframes pulse-red {{
            0% {{ opacity: 0.4; box-shadow: 0 0 4px #ef233c; }}
            50% {{ opacity: 1.0; box-shadow: 0 0 10px #ef233c; }}
            100% {{ opacity: 0.4; box-shadow: 0 0 4px #ef233c; }}
        }}

        .text-red,
        .red-accent,
        .lime-accent {{
            color: #ef233c !important;
        }}

        /* 7. Header 3-Dot Menu Popover (Border-free button) */
        div.stPopover {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
        }}
        div.stPopover > button {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: var(--text-muted) !important;
            font-size: 1.35rem !important;
            font-weight: 700 !important;
            padding: 2px 6px !important;
            min-height: 28px !important;
            height: 28px !important;
            width: 28px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
        }}
        div.stPopover > button:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            color: #ef233c !important;
            border: none !important;
            box-shadow: none !important;
        }}
        div.stPopoverBody {{
            background: #111114 !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7) !important;
            padding: 8px !important;
        }}
        div.stPopoverBody button {{
            text-align: left !important;
            justify-content: flex-start !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.88rem !important;
            border: 1px solid transparent !important;
            background: transparent !important;
            color: var(--text-primary) !important;
            padding: 8px 12px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
        }}
        div.stPopoverBody button:hover {{
            background: rgba(39, 39, 42, 0.8) !important;
            color: #ef233c !important;
            border-color: rgba(239, 35, 60, 0.3) !important;
        }}

        /* 8. Sidebar Controls (Fixed Top Controls + Scrollable History) */
        .st-key-sb_header_box {{
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 0.75rem;
            flex-shrink: 0 !important;
        }}
        .sb-brand-text {{
            font-family: 'Manrope', sans-serif;
            font-weight: 700;
            font-size: 1.15rem;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
        }}
        .sb-brand-text span {{
            color: #ef233c;
        }}

        /* Sidebar New Chat Button (Crimson Border & Glow) */
        div.st-key-btn_new_task {{
            flex-shrink: 0 !important;
        }}
        div.st-key-btn_new_task button {{
            background-color: var(--btn-new-bg) !important;
            color: var(--btn-new-fg) !important;
            border: 1px solid #ef233c !important;
            border-radius: 8px !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            padding: 8px 16px !important;
            transition: all 0.2s ease-in-out !important;
            box-shadow: 0 0 12px rgba(239, 35, 60, 0.2) !important;
        }}
        div.st-key-btn_new_task button:hover {{
            background-color: rgba(239, 35, 60, 0.12) !important;
            border-color: #ef233c !important;
            color: #ffffff !important;
            box-shadow: 0 0 22px rgba(239, 35, 60, 0.45) !important;
            transform: translateY(-1px) !important;
        }}

        /* Sidebar Model Selector */
        div.st-key-sb_model_select {{
            flex-shrink: 0 !important;
        }}
        div.st-key-sb_model_select div[data-baseweb="select"] {{
            border-radius: 8px !important;
            border: 1px solid var(--border-color) !important;
            background-color: var(--bg-card) !important;
        }}
        div.st-key-sb_model_select div[data-baseweb="select"]:hover {{
            border-color: var(--border-hover) !important;
        }}
        div.st-key-sb_model_select div[data-baseweb="select"]:focus-within {{
            border-color: #ef233c !important;
            box-shadow: 0 0 10px rgba(239, 35, 60, 0.3) !important;
        }}

        /* Recent Chats Header */
        .chats-tasks-header {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            flex-shrink: 0 !important;
        }}

        /* Sidebar Scrollable Recent Chats Container - ONLY THIS SCROLLS */
        .st-key-sb_chats_scroll {{
            flex: 1 1 auto !important;
            max-height: calc(100vh - 300px) !important;
            overflow-y: auto !important;
            padding-right: 4px !important;
        }}
        .st-key-sb_chats_scroll::-webkit-scrollbar {{
            width: 4px;
        }}
        .st-key-sb_chats_scroll::-webkit-scrollbar-thumb {{
            background: var(--border-color);
            border-radius: 4px;
        }}
        .st-key-sb_chats_scroll::-webkit-scrollbar-thumb:hover {{
            background: var(--text-muted);
        }}

        /* Chat History Buttons */
        div[class*="st-key-hist_"] button {{
            text-align: left !important;
            justify-content: flex-start !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.85rem !important;
            border: 1px solid transparent !important;
            background: transparent !important;
            color: var(--text-secondary) !important;
            padding: 6px 10px !important;
            border-radius: 6px !important;
            transition: all 0.15s ease !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }}
        div[class*="st-key-hist_"]:hover button {{
            background: var(--history-hover-bg) !important;
            color: var(--text-primary) !important;
        }}
        div[class*="st-key-hist_active_"] button {{
            background: rgba(239, 35, 60, 0.12) !important;
            color: #ef233c !important;
            border: 1px solid rgba(239, 35, 60, 0.4) !important;
            font-weight: 600 !important;
            box-shadow: 0 0 10px rgba(239, 35, 60, 0.15) !important;
        }}

        /* Delete Chat Button */
        div[class*="st-key-del_"] button {{
            background: transparent !important;
            border: none !important;
            color: var(--text-muted) !important;
            font-size: 0.8rem !important;
            padding: 4px !important;
            min-height: 24px !important;
            height: 24px !important;
            width: 24px !important;
            border-radius: 4px !important;
            transition: all 0.15s ease !important;
        }}
        div[class*="st-key-del_"] button:hover {{
            background: rgba(239, 35, 60, 0.18) !important;
            color: #ef233c !important;
        }}

        /* Sidebar Footer */
        .sidebar-footer-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 10px;
            margin-top: 10px;
            border-top: 1px solid var(--border-color);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: var(--text-muted);
        }}
        .sidebar-username {{
            font-weight: 600;
            color: var(--text-primary);
        }}
        .sidebar-gpu {{
            color: #ef233c;
        }}

        /* 9. Hero Section */
        .hero-container {{
            text-align: left;
            margin-top: 1.5rem;
            margin-bottom: 2rem;
        }}
        .hero-title {{
            font-family: 'Manrope', sans-serif !important;
            font-size: 2.3rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.15;
            color: var(--text-primary);
            margin-bottom: 0.4rem;
        }}
        .hero-subtitle {{
            font-family: 'Inter', sans-serif;
            font-size: 0.98rem;
            color: var(--text-secondary);
            font-weight: 400;
            letter-spacing: -0.01em;
        }}

        /* 10. Suggestion Cards (Dark Zinc Cards with Red Hover Glow & Manrope Titles) */
        div.st-key-card_py button,
        div.st-key-card_sheet button,
        div.st-key-card_doc button,
        div.st-key-card_rag button {{
            text-align: left !important;
            justify-content: flex-start !important;
            background: rgba(24, 24, 27, 0.65) !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            border-radius: 12px !important;
            padding: 16px 18px !important;
            min-height: 96px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.88rem !important;
            line-height: 1.4 !important;
            color: var(--text-secondary) !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
        }}
        div.st-key-card_py button:hover,
        div.st-key-card_sheet button:hover,
        div.st-key-card_doc button:hover,
        div.st-key-card_rag button:hover {{
            background: rgba(39, 39, 42, 0.8) !important;
            border-color: #ef233c !important;
            color: var(--text-primary) !important;
            box-shadow: 0 0 25px rgba(239, 35, 60, 0.25), 0 8px 24px rgba(0, 0, 0, 0.4) !important;
            transform: translateY(-2px) !important;
        }}
        div.st-key-card_py button strong,
        div.st-key-card_sheet button strong,
        div.st-key-card_doc button strong,
        div.st-key-card_rag button strong {{
            display: block !important;
            font-family: 'Manrope', sans-serif !important;
            font-size: 0.98rem !important;
            font-weight: 700 !important;
            color: var(--text-primary) !important;
            margin-bottom: 5px !important;
        }}

        /* 11. Message Cards & Thread Styling */
        div[data-testid="stChatMessage"] {{
            background: rgba(24, 24, 27, 0.65) !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            border-radius: 12px !important;
            padding: 16px 20px !important;
            margin-bottom: 1.25rem !important;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
            backdrop-filter: blur(8px) !important;
            -webkit-backdrop-filter: blur(8px) !important;
        }}
        div[data-testid="stChatMessage"]:hover {{
            border-color: rgba(255, 255, 255, 0.16) !important;
        }}
        div[data-testid="stChatMessageContent"] {{
            font-family: 'Inter', sans-serif !important;
            font-size: 0.94rem !important;
            line-height: 1.6 !important;
        }}
        div[data-testid="stChatMessageContent"] pre,
        div[data-testid="stChatMessageContent"] code {{
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 0.86rem !important;
        }}

        /* 12. Floating Chat Bar (Single Uniform Background Inside Border) */
        div[data-testid="stBottom"] {{
            background: transparent !important;
            border-top: none !important;
            padding: 0 0 16px 0 !important;
        }}
        div[data-testid="stBottom"] > div {{
            background: transparent !important;
            max-width: 860px !important;
            margin: 0 auto !important;
        }}
        div[data-testid="stChatInput"] {{
            max-width: 860px !important;
            margin: 0 auto !important;
            border-radius: 24px !important;
            background: #0e0e11 !important;
            background-color: #0e0e11 !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5) !important;
            padding: 4px 10px !important;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1) !important;
        }}
        div[data-testid="stChatInput"]:hover {{
            border-color: rgba(255, 255, 255, 0.28) !important;
            box-shadow: 0 10px 36px rgba(0, 0, 0, 0.6) !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stChatInput"]:focus-within {{
            border-color: #ef233c !important;
            box-shadow: 0 0 20px rgba(239, 35, 60, 0.35) !important;
        }}
        /* Remove any inner box backgrounds so there is ONLY ONE color inside border */
        div[data-testid="stChatInput"] > div,
        div[data-testid="stChatInput"] > div > div,
        div[data-testid="stChatInput"] [data-baseweb="base-input"],
        div[data-testid="stChatInput"] [data-baseweb="textarea"] {{
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        div[data-testid="stChatInput"] textarea {{
            background: transparent !important;
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 0.94rem !important;
            text-align: left !important;
            padding: 8px 6px !important;
        }}
        div[data-testid="stChatInput"] button {{
            border-radius: 50% !important;
            background: #ef233c !important;
            background-color: #ef233c !important;
            color: #ffffff !important;
            border: none !important;
            transition: all 0.2s ease !important;
            font-weight: 700 !important;
            width: 32px !important;
            height: 32px !important;
            min-width: 32px !important;
        }}
        div[data-testid="stChatInput"] button:hover {{
            transform: scale(1.08) !important;
            background: #d90429 !important;
            background-color: #d90429 !important;
            box-shadow: 0 0 16px rgba(239, 35, 60, 0.6) !important;
        }}

        /* 13. Deliverables & Action Buttons */
        div[data-testid="stDownloadButton"] button {{
            background-color: rgba(239, 35, 60, 0.1) !important;
            color: #ef233c !important;
            border: 1px solid rgba(239, 35, 60, 0.4) !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stDownloadButton"] button:hover {{
            background-color: #ef233c !important;
            color: #ffffff !important;
            border-color: #ef233c !important;
            box-shadow: 0 0 16px rgba(239, 35, 60, 0.4) !important;
        }}
        div[data-testid="stLinkButton"] a {{
            background-color: rgba(24, 24, 27, 0.8) !important;
            color: var(--text-secondary) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 8px !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.2s ease !important;
        }}
        div[data-testid="stLinkButton"] a:hover {{
            border-color: #ef233c !important;
            color: #ef233c !important;
        }}

        /* 14. Section Header (Deliverables, Knowledge Base, Models, Audit) */
        .section-header {{
            margin-bottom: 1.5rem;
        }}
        .section-header h2 {{
            font-family: 'Manrope', sans-serif !important;
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
        }}
        .section-header p {{
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            color: var(--text-muted);
            margin-top: 0;
        }}

        /* 15. Disclaimer Footer */
        .disclaimer {{
            text-align: center;
            font-family: 'Inter', sans-serif;
            font-size: 0.74rem;
            color: var(--text-muted);
            margin-top: 0.85rem;
        }}
    </style>
    """, unsafe_allow_html=True)
