from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class UploadState:
    filenames: list[str]


def render_file_uploader() -> UploadState:
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown("### File upload")
    st.caption("Upload source files, diffs, or notes for local review composition.")

    uploads = st.file_uploader(
        "Attach files",
        accept_multiple_files=True,
        help="Select one or more local files for the review workspace.",
        label_visibility="collapsed",
    )

    filenames = [file.name for file in uploads] if uploads else []
    if filenames:
        st.success(f"Loaded {len(filenames)} file(s): {', '.join(filenames)}")
    else:
        st.info("No files uploaded yet.")

    st.markdown("</div>", unsafe_allow_html=True)
    return UploadState(filenames=filenames)
