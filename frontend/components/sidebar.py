from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class SidebarState:
    theme: str
    language: str
    review_context: str


SUPPORTED_LANGUAGES = ["Python", "JavaScript", "TypeScript", "Go", "Java", "Rust", "YAML", "Markdown"]
SUPPORTED_THEMES = ["Aurora", "Slate", "Sunrise"]


def render_sidebar() -> SidebarState:
    with st.sidebar:
        st.markdown("## AI Code Reviewer")
        st.caption("Frontend workspace for local review composition.")
        st.markdown("---")
        theme = st.radio("Theme", SUPPORTED_THEMES, index=0, help="Switch the visual style of the review workspace.")
        language = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=0,
            help="Choose the language used for the code editor preview.",
        )
        review_context = st.text_area(
            "Review context",
            placeholder="Add architecture notes, conventions, or goals for the review...",
            height=160,
            help="Provide local context that will shape the review summary placeholders.",
        )
        st.markdown("---")
        st.caption("Review context is sent to the AI model along with your code.")

    return SidebarState(theme=theme, language=language, review_context=review_context.strip())