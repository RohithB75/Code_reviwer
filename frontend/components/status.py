from __future__ import annotations

from collections.abc import Iterable

import streamlit as st
from services.api_service import ApiResponse


def render_status_panel(
    *,
    review_clicked: bool,
    language: str,
    theme: str,
    uploaded_files: Iterable[str],
    code: str,
    backend_health: ApiResponse | None,
) -> None:
    uploaded_list = list(uploaded_files)
    line_count = len(code.splitlines()) if code else 0
    char_count = len(code)

    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown("### Status")

    if review_clicked:
        if backend_health and backend_health.ok:
            st.success("Review composition ready. Backend health check succeeded.")
        elif backend_health and not backend_health.ok:
            st.error(backend_health.error or "Backend health check failed.")
        else:
            st.success("Review composition ready.")
    else:
        st.info("Make selections, add code, and choose Review code to check backend connectivity.")

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            f'<div class="panel-card"><div class="panel-label">Theme</div><div class="panel-value">{theme}</div></div>',
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            f'<div class="panel-card"><div class="panel-label">Language</div><div class="panel-value">{language}</div></div>',
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            f'<div class="panel-card"><div class="panel-label">Files</div><div class="panel-value">{len(uploaded_list)}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f'<div class="stream-status">Lines: {line_count} | Characters: {char_count} | Uploaded: {", ".join(uploaded_list) if uploaded_list else "none"}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
