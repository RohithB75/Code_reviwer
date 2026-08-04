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
    review_result: dict | None = None,
    review_error: str | None = None,
    performance_clicked: bool = False,
    performance_result: dict | None = None,
    performance_error: str | None = None,
    security_clicked: bool = False,
    security_result: dict | None = None,
    security_error: str | None = None,
    refactoring_clicked: bool = False,
    refactoring_result: dict | None = None,
    refactoring_error: str | None = None,
    unit_tests_clicked: bool = False,
    unit_tests_result: dict | None = None,
    unit_tests_error: str | None = None,
    documentation_clicked: bool = False,
    documentation_result: dict | None = None,
    documentation_error: str | None = None,
) -> None:
    st.markdown('<div class="app-shell">', unsafe_allow_html=True)
    st.markdown("### Output")
    tabs = st.tabs(
        [
            "Summary",
            "Performance",
            "Security",
            "Refactoring",
            "Unit Tests",
            "Documentation",
            "Backend",
            "Context",
            "Preview",
        ]
    )

    with tabs[0]:
        if not review_clicked:
            st.info("Review the code to populate the summary tab.")
        elif review_error:
            st.error(review_error)
        elif review_result:
            st.write(f"**Language:** {review_result.get('language', language)}")
            st.write(f"**Quality score:** {review_result.get('quality_score', 'n/a')}/100")
            st.markdown("**Summary**")
            st.write(review_result.get("summary", ""))
            suggestions = review_result.get("suggestions") or []
            if suggestions:
                st.markdown("**Suggestions**")
                for suggestion in suggestions:
                    st.markdown(f"- {suggestion}")
        else:
            st.info("Waiting for review result...")

    with tabs[1]:
        if not performance_clicked:
            st.info("Click \"Analyze performance\" to get time/space complexity and optimization suggestions.")
        elif performance_error:
            st.error(performance_error)
        elif performance_result:
            st.write(f"**Language:** {performance_result.get('language', language)}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Time complexity", performance_result.get("time_complexity", "Unknown"))
            with col_b:
                st.metric("Space complexity", performance_result.get("space_complexity", "Unknown"))
            if performance_result.get("memory_usage"):
                st.write(f"**Memory usage:** {performance_result['memory_usage']}")
            st.markdown("**Summary**")
            st.write(performance_result.get("summary", ""))

            inefficient_loops = performance_result.get("inefficient_loops") or []
            if inefficient_loops:
                st.markdown("**Inefficient loops**")
                for item in inefficient_loops:
                    st.markdown(f"- {item}")

            duplicate_work = performance_result.get("duplicate_work") or []
            if duplicate_work:
                st.markdown("**Duplicate work**")
                for item in duplicate_work:
                    st.markdown(f"- {item}")

            better_algorithms = performance_result.get("better_algorithms") or []
            if better_algorithms:
                st.markdown("**Suggested improvements**")
                for item in better_algorithms:
                    st.markdown(f"- {item}")
        else:
            st.info("Waiting for performance result...")

    with tabs[2]:
        if not security_clicked:
            st.info("Click \"Run security review\" to scan for vulnerabilities.")
        elif security_error:
            st.error(security_error)
        elif security_result:
            st.write(f"**Language:** {security_result.get('language', language)}")
            st.write(f"**Overall severity:** {security_result.get('overall_severity', 'Unknown')}")
            st.markdown("**Summary**")
            st.write(security_result.get("summary", ""))
            findings = security_result.get("findings") or []
            if findings:
                st.markdown("**Findings**")
                for finding in findings:
                    with st.expander(f"{finding.get('severity', '?')} — {finding.get('issue', 'Issue')}"):
                        st.write(f"**Description:** {finding.get('description', '')}")
                        st.write(f"**Evidence:** {finding.get('evidence', '')}")
                        st.write(f"**Recommendation:** {finding.get('recommendation', '')}")
            else:
                st.success("No specific findings reported.")
        else:
            st.info("Waiting for security review result...")

    with tabs[3]:
        if not refactoring_clicked:
            st.info("Click \"Suggest refactoring\" to get an improved version of the code.")
        elif refactoring_error:
            st.error(refactoring_error)
        elif refactoring_result:
            st.write(f"**Language:** {refactoring_result.get('language', language)}")
            st.markdown("**Summary**")
            st.write(refactoring_result.get("summary", ""))
            changes = refactoring_result.get("changes") or []
            if changes:
                st.markdown("**Changes**")
                for change in changes:
                    st.markdown(f"- {change}")
            improved_code = refactoring_result.get("improved_code", "")
            if improved_code:
                st.markdown("**Improved code**")
                st.code(improved_code, language=language.lower())
        else:
            st.info("Waiting for refactoring result...")

    with tabs[4]:
        if not unit_tests_clicked:
            st.info("Click \"Generate unit tests\" to get pytest tests for this code.")
        elif unit_tests_error:
            st.error(unit_tests_error)
        elif unit_tests_result:
            st.write(f"**Language:** {unit_tests_result.get('language', language)}")
            st.markdown("**Summary**")
            st.write(unit_tests_result.get("summary", ""))
            test_code = unit_tests_result.get("test_code", "")
            if test_code:
                st.code(test_code, language="python")
        else:
            st.info("Waiting for generated tests...")

    with tabs[5]:
        if not documentation_clicked:
            st.info("Click \"Generate documentation\" to get Markdown docs for this code.")
        elif documentation_error:
            st.error(documentation_error)
        elif documentation_result:
            st.write(f"**Language:** {documentation_result.get('language', language)}")
            st.markdown("**Summary**")
            st.write(documentation_result.get("summary", ""))
            markdown_doc = documentation_result.get("markdown_documentation", "")
            if markdown_doc:
                st.markdown(markdown_doc)
        else:
            st.info("Waiting for documentation...")

    with tabs[6]:
        if backend_health is None:
            st.info("Run a review to call the backend health endpoint.")
        elif backend_health.ok:
            st.success("Backend health endpoint responded successfully.")
            st.json(backend_health.data)
        else:
            st.error(backend_health.error or "Backend health endpoint failed.")
            st.write(backend_health_message)

    with tabs[7]:
        if review_context:
            st.write(review_context)
        else:
            st.caption("No additional context provided.")

    with tabs[8]:
        st.code(code or "# Your code preview will appear here.", language=language.lower())

    st.markdown("</div>", unsafe_allow_html=True)