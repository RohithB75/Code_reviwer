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


def _run_action(
    *,
    api_service: ApiService,
    method_name: str,
    state_key: str,
    spinner_text: str,
    success_text: str,
    editor_code: str,
    file_name: str | None,
    review_context: str,
    language: str,
) -> None:
    st.session_state[f"{state_key}_clicked"] = True
    if not editor_code:
        st.session_state[f"{state_key}_result"] = None
        st.session_state[f"{state_key}_error"] = "No code to analyze. Paste code or upload a file first."
        st.warning(st.session_state[f"{state_key}_error"])
        return

    method = getattr(api_service, method_name)
    with st.spinner(spinner_text):
        result = method(
            source_code=editor_code,
            file_name=file_name,
            review_context=review_context,
            language_hint=language,
        )

    if result.ok:
        st.session_state[f"{state_key}_result"] = result.data
        st.session_state[f"{state_key}_error"] = None
        st.success(success_text)
    else:
        st.session_state[f"{state_key}_result"] = None
        st.session_state[f"{state_key}_error"] = result.error or f"{spinner_text} failed."
        st.error(st.session_state[f"{state_key}_error"])


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
    st.session_state.setdefault("review_result", None)
    st.session_state.setdefault("review_error", None)
    st.session_state.setdefault("performance_result", None)
    st.session_state.setdefault("performance_error", None)
    st.session_state.setdefault("performance_clicked", False)
    st.session_state.setdefault("security_result", None)
    st.session_state.setdefault("security_error", None)
    st.session_state.setdefault("security_clicked", False)
    st.session_state.setdefault("refactoring_result", None)
    st.session_state.setdefault("refactoring_error", None)
    st.session_state.setdefault("refactoring_clicked", False)
    st.session_state.setdefault("unit_tests_result", None)
    st.session_state.setdefault("unit_tests_error", None)
    st.session_state.setdefault("unit_tests_clicked", False)
    st.session_state.setdefault("documentation_result", None)
    st.session_state.setdefault("documentation_error", None)
    st.session_state.setdefault("documentation_clicked", False)

    sidebar_state = render_sidebar()
    apply_theme(sidebar_state.theme)

    render_header(sidebar_state)

    # Uploader runs first so its content can pre-fill the editor below.
    upload_state = render_file_uploader()
    first_uploaded_content = next(iter(upload_state.contents.values()), None)
    editor_state = render_code_editor(sidebar_state.language, uploaded_content=first_uploaded_content)

    st.session_state["uploaded_files"] = upload_state.filenames

    api_service = ApiService(base_url=os.getenv("BACKEND_BASE_URL", "http://localhost:8000"))

    review_clicked = st.button("Review code", use_container_width=True, type="primary")
    if review_clicked:
        st.session_state["review_clicked"] = True

        with st.spinner("Checking backend health..."):
            health_result = api_service.health_check()
        st.session_state["backend_health"] = health_result

        if not health_result.ok:
            st.session_state["backend_health_message"] = health_result.error or "Backend health check failed."
            st.session_state["review_result"] = None
            st.session_state["review_error"] = st.session_state["backend_health_message"]
            st.error(st.session_state["backend_health_message"])
        elif not editor_state.code:
            st.session_state["backend_health_message"] = "Backend health check succeeded."
            st.session_state["review_result"] = None
            st.session_state["review_error"] = "No code to review. Paste code or upload a file first."
            st.warning(st.session_state["review_error"])
        else:
            st.session_state["backend_health_message"] = "Backend health check succeeded."
            file_name = upload_state.filenames[0] if upload_state.filenames else None
            with st.spinner("Sending code to the AI review model..."):
                review_result = api_service.analyze_review(
                    source_code=editor_state.code,
                    file_name=file_name,
                    review_context=sidebar_state.review_context,
                    language_hint=sidebar_state.language,
                )

            if review_result.ok:
                st.session_state["review_result"] = review_result.data
                st.session_state["review_error"] = None
                st.success("Review complete.")
            else:
                st.session_state["review_result"] = None
                st.session_state["review_error"] = review_result.error or "Review request failed."
                st.error(st.session_state["review_error"])
    elif st.session_state["backend_health"] is None:
        st.caption("Click Review code to run the AI review.")

    performance_clicked = st.button(
        "Analyze performance (time/space complexity)",
        use_container_width=True,
    )
    if performance_clicked:
        file_name = upload_state.filenames[0] if upload_state.filenames else None
        _run_action(
            api_service=api_service,
            method_name="analyze_performance",
            state_key="performance",
            spinner_text="Analyzing time/space complexity...",
            success_text="Performance analysis complete.",
            editor_code=editor_state.code,
            file_name=file_name,
            review_context=sidebar_state.review_context,
            language=sidebar_state.language,
        )

    security_clicked = st.button("Run security review", use_container_width=True)
    if security_clicked:
        file_name = upload_state.filenames[0] if upload_state.filenames else None
        _run_action(
            api_service=api_service,
            method_name="analyze_security",
            state_key="security",
            spinner_text="Scanning for security issues...",
            success_text="Security review complete.",
            editor_code=editor_state.code,
            file_name=file_name,
            review_context=sidebar_state.review_context,
            language=sidebar_state.language,
        )

    refactoring_clicked = st.button("Suggest refactoring", use_container_width=True)
    if refactoring_clicked:
        file_name = upload_state.filenames[0] if upload_state.filenames else None
        _run_action(
            api_service=api_service,
            method_name="analyze_refactoring",
            state_key="refactoring",
            spinner_text="Generating refactored code...",
            success_text="Refactoring suggestion ready.",
            editor_code=editor_state.code,
            file_name=file_name,
            review_context=sidebar_state.review_context,
            language=sidebar_state.language,
        )

    unit_tests_clicked = st.button("Generate unit tests", use_container_width=True)
    if unit_tests_clicked:
        file_name = upload_state.filenames[0] if upload_state.filenames else None
        _run_action(
            api_service=api_service,
            method_name="generate_unit_tests",
            state_key="unit_tests",
            spinner_text="Generating pytest unit tests...",
            success_text="Unit tests generated.",
            editor_code=editor_state.code,
            file_name=file_name,
            review_context=sidebar_state.review_context,
            language=sidebar_state.language,
        )

    documentation_clicked = st.button("Generate documentation", use_container_width=True)
    if documentation_clicked:
        file_name = upload_state.filenames[0] if upload_state.filenames else None
        _run_action(
            api_service=api_service,
            method_name="generate_documentation",
            state_key="documentation",
            spinner_text="Generating documentation...",
            success_text="Documentation generated.",
            editor_code=editor_state.code,
            file_name=file_name,
            review_context=sidebar_state.review_context,
            language=sidebar_state.language,
        )

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
        review_result=st.session_state["review_result"],
        review_error=st.session_state["review_error"],
        performance_clicked=st.session_state["performance_clicked"],
        performance_result=st.session_state["performance_result"],
        performance_error=st.session_state["performance_error"],
        security_clicked=st.session_state["security_clicked"],
        security_result=st.session_state["security_result"],
        security_error=st.session_state["security_error"],
        refactoring_clicked=st.session_state["refactoring_clicked"],
        refactoring_result=st.session_state["refactoring_result"],
        refactoring_error=st.session_state["refactoring_error"],
        unit_tests_clicked=st.session_state["unit_tests_clicked"],
        unit_tests_result=st.session_state["unit_tests_result"],
        unit_tests_error=st.session_state["unit_tests_error"],
        documentation_clicked=st.session_state["documentation_clicked"],
        documentation_result=st.session_state["documentation_result"],
        documentation_error=st.session_state["documentation_error"],
    )


build_page()