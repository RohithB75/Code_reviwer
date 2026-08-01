from __future__ import annotations

import streamlit as st

from services.api_service import ApiResponse


def render_output_tabs(
    *,
    review_clicked: bool,
    language: str,
    code: str,
    uploaded_files: list[str],
    review_context: str,
    backend_health: ApiResponse | None,
    backend_health_message: str,
) -> None:
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown("### Output")
    tabs = st.tabs(["Summary", "Backend", "Context", "Preview"])

    with tabs[0]:
        if review_clicked:
            st.success("Local review draft generated.")
            st.write(f"Language: {language}")
            st.write(f"Code length: {len(code)} characters")
            st.write(f"Uploaded files: {len(uploaded_files)}")
        else:
            st.info("Review the code to populate the summary tab.")

    with tabs[1]:
        if backend_health is None:
            st.info("Run a review to call the backend health endpoint.")
        elif backend_health.ok:
            st.success("Backend health endpoint responded successfully.")
            st.json(backend_health.data)
        else:
            st.error(backend_health.error or "Backend health endpoint failed.")
            st.write(backend_health_message)

    with tabs[2]:
        if review_context:
            st.write(review_context)
        else:
            st.caption("No additional context provided.")

    with tabs[3]:
        st.code(code or "# Your code preview will appear here.", language=language.lower())

    st.markdown("</div>", unsafe_allow_html=True)
