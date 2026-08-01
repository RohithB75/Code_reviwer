from __future__ import annotations

import streamlit as st

from components.sidebar import SidebarState


def render_header(state: SidebarState) -> None:
    st.markdown(
        '<div class="app-shell">'
        '<div class="hero-title">AI Code Reviewer</div>'
        '<div class="hero-copy">A polished local review workspace for composing code review inputs, uploading files, and preparing output views before the backend is connected.</div>'
        '<div class="pill-row">'
        f'<span class="pill">Theme: {state.theme}</span>'
        f'<span class="pill">Language: {state.language}</span>'
        '<span class="pill">Backend disconnected</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.write("")
