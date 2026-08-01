from __future__ import annotations

import streamlit as st


THEMES: dict[str, dict[str, str]] = {
    "Aurora": {
        "bg": "#08111f",
        "surface": "rgba(12, 20, 35, 0.82)",
        "surface_alt": "rgba(15, 27, 48, 0.95)",
        "border": "rgba(130, 170, 255, 0.18)",
        "text": "#f4f7fb",
        "muted": "#9fb0c7",
        "accent": "#7dd3fc",
        "accent_soft": "rgba(125, 211, 252, 0.18)",
        "success": "#34d399",
        "warning": "#fbbf24",
        "danger": "#fb7185",
        "glow": "radial-gradient(circle at top right, rgba(125,211,252,0.28), transparent 34%), radial-gradient(circle at bottom left, rgba(52,211,153,0.16), transparent 30%)",
    },
    "Slate": {
        "bg": "#0f172a",
        "surface": "rgba(17, 24, 39, 0.86)",
        "surface_alt": "rgba(30, 41, 59, 0.96)",
        "border": "rgba(148, 163, 184, 0.16)",
        "text": "#eef2ff",
        "muted": "#cbd5e1",
        "accent": "#38bdf8",
        "accent_soft": "rgba(56, 189, 248, 0.16)",
        "success": "#22c55e",
        "warning": "#eab308",
        "danger": "#f87171",
        "glow": "radial-gradient(circle at top left, rgba(56,189,248,0.22), transparent 32%), radial-gradient(circle at bottom right, rgba(148,163,184,0.13), transparent 32%)",
    },
    "Sunrise": {
        "bg": "#1b1328",
        "surface": "rgba(31, 22, 47, 0.86)",
        "surface_alt": "rgba(52, 31, 78, 0.96)",
        "border": "rgba(251, 191, 36, 0.16)",
        "text": "#fff7ed",
        "muted": "#e7d5b8",
        "accent": "#fb923c",
        "accent_soft": "rgba(251, 146, 60, 0.18)",
        "success": "#4ade80",
        "warning": "#f59e0b",
        "danger": "#fb7185",
        "glow": "radial-gradient(circle at top right, rgba(251,146,60,0.22), transparent 32%), radial-gradient(circle at bottom left, rgba(251,191,36,0.12), transparent 30%)",
    },
}


def apply_theme(theme_name: str) -> None:
    theme = THEMES.get(theme_name, THEMES["Aurora"])
    st.markdown(
        f"""
        <style>
            :root {{
                --ui-bg: {theme["bg"]};
                --ui-surface: {theme["surface"]};
                --ui-surface-alt: {theme["surface_alt"]};
                --ui-border: {theme["border"]};
                --ui-text: {theme["text"]};
                --ui-muted: {theme["muted"]};
                --ui-accent: {theme["accent"]};
                --ui-accent-soft: {theme["accent_soft"]};
                --ui-success: {theme["success"]};
                --ui-warning: {theme["warning"]};
                --ui-danger: {theme["danger"]};
                --ui-glow: {theme["glow"]};
            }}

            .stApp {{
                background: var(--ui-bg);
                color: var(--ui-text);
                background-image: var(--ui-glow);
                background-attachment: fixed;
            }}

            .stApp::before {{
                content: "";
                position: fixed;
                inset: 0;
                pointer-events: none;
                background-image: linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
                background-size: 44px 44px;
                mask-image: linear-gradient(to bottom, rgba(0,0,0,0.48), transparent 80%);
                opacity: 0.3;
            }}

            section[data-testid="stSidebar"] {{
                background: rgba(6, 10, 19, 0.7);
                border-right: 1px solid var(--ui-border);
            }}

            .app-shell {{
                border: 1px solid var(--ui-border);
                background: var(--ui-surface);
                border-radius: 24px;
                padding: 1.25rem 1.35rem;
                box-shadow: 0 28px 80px rgba(0, 0, 0, 0.28);
                backdrop-filter: blur(16px);
            }}

            .hero-title {{
                font-size: 3rem;
                line-height: 1.02;
                font-weight: 800;
                letter-spacing: -0.04em;
                margin-bottom: 0.5rem;
                color: var(--ui-text);
            }}

            .hero-copy {{
                color: var(--ui-muted);
                max-width: 68ch;
                font-size: 1rem;
            }}

            .pill-row {{
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-top: 1rem;
            }}

            .pill {{
                border: 1px solid var(--ui-border);
                background: var(--ui-surface-alt);
                border-radius: 999px;
                padding: 0.35rem 0.75rem;
                color: var(--ui-text);
                font-size: 0.84rem;
            }}

            .panel-card {{
                border: 1px solid var(--ui-border);
                border-radius: 20px;
                background: var(--ui-surface);
                padding: 1rem 1.1rem;
            }}

            .panel-label {{
                color: var(--ui-muted);
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
                margin-bottom: 0.35rem;
            }}

            .panel-value {{
                color: var(--ui-text);
                font-size: 1.12rem;
                font-weight: 700;
            }}

            .status-chip {{
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                padding: 0.38rem 0.7rem;
                border-radius: 999px;
                border: 1px solid var(--ui-border);
                background: var(--ui-surface-alt);
                color: var(--ui-text);
                font-size: 0.84rem;
            }}

            .status-chip strong {{
                color: var(--ui-accent);
            }}

            .stTextArea textarea {{
                background: rgba(0, 0, 0, 0.15) !important;
                color: var(--ui-text) !important;
                border-radius: 16px !important;
                border: 1px solid var(--ui-border) !important;
            }}

            .stButton>button {{
                border-radius: 14px !important;
                padding: 0.7rem 1.15rem !important;
                border: 1px solid var(--ui-border) !important;
                background: linear-gradient(135deg, var(--ui-accent), rgba(255,255,255,0.08)) !important;
                color: #06111f !important;
                font-weight: 700 !important;
            }}

            .stButton>button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.4rem;
            }}

            .stTabs [data-baseweb="tab"] {{
                border-radius: 999px !important;
                border: 1px solid var(--ui-border) !important;
                background: var(--ui-surface-alt) !important;
                color: var(--ui-muted) !important;
            }}

            .stTabs [aria-selected="true"] {{
                color: var(--ui-text) !important;
                border-color: var(--ui-accent) !important;
                background: var(--ui-accent-soft) !important;
            }}

            .stream-status {{
                border-left: 4px solid var(--ui-accent);
                padding: 0.85rem 1rem;
                border-radius: 14px;
                background: rgba(255,255,255,0.03);
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
