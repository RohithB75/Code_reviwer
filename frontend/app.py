from __future__ import annotations

import os

import streamlit as st

from components.editor import render_code_editor
from components.header import render_header
from components.output_tabs import render_output_tabs
from components.sidebar import render_sidebar
from components.status import render_status_panel
from components.theme import apply_theme
from components.uploader import render_file_uploader
from services.api_service import ApiService


def build_page() -> None:
    st.set_page_config(
        page_title="AI Code Reviewer",
        page_icon="AI",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.session_state.setdefault("review_clicked", False)
    st.session_state.setdefault("uploaded_files", [])
    st.session_state.setdefault("backend_health", None)
    st.session_state.setdefault("backend_health_message", "Backend not checked yet.")

    sidebar_state = render_sidebar()
    apply_theme(sidebar_state.theme)

    render_header(sidebar_state)

    editor_state = render_code_editor(sidebar_state.language)
    upload_state = render_file_uploader()

    st.session_state["uploaded_files"] = upload_state.filenames

    api_service = ApiService(base_url=os.getenv("BACKEND_BASE_URL", "http://localhost:8000"))

    review_clicked = st.button("Review code", use_container_width=True, type="primary")
    if review_clicked:
        st.session_state["review_clicked"] = True
        with st.spinner("Checking backend health..."):
            health_result = api_service.health_check()

        st.session_state["backend_health"] = health_result
        if health_result.ok:
            st.session_state["backend_health_message"] = "Backend health check succeeded."
            st.success("Connected to the backend health endpoint.")
        else:
            st.session_state["backend_health_message"] = health_result.error or "Backend health check failed."
            st.error(st.session_state["backend_health_message"])
    elif st.session_state["backend_health"] is None:
        st.caption("Click Review code to check backend connectivity.")

    render_status_panel(
        review_clicked=st.session_state["review_clicked"],
        language=sidebar_state.language,
        theme=sidebar_state.theme,
        uploaded_files=upload_state.filenames,
        code=editor_state.code,
        backend_health=st.session_state["backend_health"],
    )
    render_output_tabs(
        review_clicked=st.session_state["review_clicked"],
        language=sidebar_state.language,
        code=editor_state.code,
        uploaded_files=upload_state.filenames,
        review_context=sidebar_state.review_context,
        backend_health=st.session_state["backend_health"],
        backend_health_message=st.session_state["backend_health_message"],
    )


build_page()
