from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from app.application.services.review_engine import (
    DocumentationAnalysis,
    PerformanceAnalysis,
    RefactoringAnalysis,
    ReviewEngine,
    ReviewAnalysis,
    SecurityAnalysis,
    UnitTestGenerationAnalysis,
    documentation_has_required_sections,
    build_fallback_documentation_markdown,
)
from app.schemas.report import ReportExportMetadata


@dataclass(frozen=True)
class ReportAnalysis:
    executive_summary: str
    quality: dict[str, Any]
    security: dict[str, Any]
    performance: dict[str, Any]
    refactoring: dict[str, Any]
    tests: dict[str, Any]
    documentation: dict[str, Any]
    overall_score: int
    markdown_report: str


REPORT_SECTION_ORDER: tuple[str, ...] = (
    "executive_summary",
    "quality",
    "security",
    "performance",
    "refactoring",
    "tests",
    "documentation",
    "overall_score",
)


class ReportEngine:
    def __init__(self, review_engine: ReviewEngine) -> None:
        self.review_engine = review_engine
        self.logger = logging.getLogger(__name__)

    def generate_report(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> ReportAnalysis:
        """Run every analysis flow and combine the results into a single report."""
        # Run each analysis defensively; if one fails to parse or the LLM fails,
        # continue with fallback minimal sections so the report still returns.
        try:
            quality = self.review_engine.review_source_code(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:  # keep broad to catch parse/LLM errors
            self.logger.warning("Quality analysis failed: %s", exc)
            quality = ReviewAnalysis(language="Unknown", summary="Quality analysis failed.", suggestions=[], quality_score=0)

        try:
            security = self.review_engine.security_review_source_code(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:
            self.logger.warning("Security analysis failed: %s", exc)
            security = SecurityAnalysis(language="Unknown", summary="Security analysis failed.", overall_severity="Low", findings=[])

        try:
            performance = self.review_engine.performance_analysis_source_code(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:
            self.logger.warning("Performance analysis failed: %s", exc)
            performance = PerformanceAnalysis(
                language="Unknown",
                summary="Performance analysis failed.",
                time_complexity="Unknown",
                space_complexity="Unknown",
                memory_usage="",
                inefficient_loops=[],
                duplicate_work=[],
                better_algorithms=[],
            )

        try:
            refactoring = self.review_engine.refactor_source_code(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:
            self.logger.warning("Refactoring analysis failed: %s", exc)
            refactoring = RefactoringAnalysis(language="Unknown", summary="Refactoring analysis failed.", changes=[], improved_code="")

        try:
            tests = self.review_engine.generate_unit_tests(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:
            self.logger.warning("Unit test generation failed: %s", exc)
            tests = UnitTestGenerationAnalysis(language="Unknown", summary="Test generation failed.", test_code="")

        try:
            documentation = self.review_engine.generate_documentation(
                source_code,
                file_name=file_name,
                review_context=review_context,
                language_hint=language_hint,
            )
        except Exception as exc:
            self.logger.warning("Documentation generation failed: %s", exc)
            documentation = DocumentationAnalysis(language="Unknown", summary="Documentation generation failed.", markdown_documentation=build_fallback_documentation_markdown(source_code, language="Unknown", file_name=file_name or "<unknown>", review_context=review_context))

        quality_section = build_quality_section(quality)
        security_section = build_security_section(security)
        performance_section = build_performance_section(performance)
        refactoring_section = build_refactoring_section(refactoring)
        tests_section = build_tests_section(tests)
        documentation_section = build_documentation_section(documentation)

        overall_score = calculate_overall_score(
            quality_section["score"],
            security_section["score"],
            performance_section["score"],
            refactoring_section["score"],
            tests_section["score"],
            documentation_section["score"],
        )

        markdown_report = render_markdown_report(
            file_name=file_name or "<unknown>",
            executive_summary=build_executive_summary(
                quality_section,
                security_section,
                performance_section,
                refactoring_section,
                tests_section,
                documentation_section,
                overall_score,
            ),
            quality_section=quality_section,
            security_section=security_section,
            performance_section=performance_section,
            refactoring_section=refactoring_section,
            tests_section=tests_section,
            documentation_section=documentation_section,
            overall_score=overall_score,
            review_context=review_context,
        )

        return ReportAnalysis(
            executive_summary=build_executive_summary(
                quality_section,
                security_section,
                performance_section,
                refactoring_section,
                tests_section,
                documentation_section,
                overall_score,
            ),
            quality=quality_section,
            security=security_section,
            performance=performance_section,
            refactoring=refactoring_section,
            tests=tests_section,
            documentation=documentation_section,
            overall_score=overall_score,
            markdown_report=markdown_report,
        )

    def build_report_payload(self, analysis: ReportAnalysis) -> dict[str, Any]:
        """Convert the assembled report into a serializable JSON payload."""
        return {
            "executive_summary": analysis.executive_summary,
            "quality": analysis.quality,
            "security": analysis.security,
            "performance": analysis.performance,
            "refactoring": analysis.refactoring,
            "tests": analysis.tests,
            "documentation": analysis.documentation,
            "overall_score": analysis.overall_score,
        }

    def build_report_export_metadata(self, analysis: ReportAnalysis) -> ReportExportMetadata:
        """Build export metadata that can be reused by a future PDF export flow."""
        return ReportExportMetadata(
            pdf_export_ready=bool(analysis.markdown_report.strip()),
            markdown_report=analysis.markdown_report,
            json_report=self.build_report_payload(analysis),
        )

    def build_report_markdown(self, analysis: ReportAnalysis) -> str:
        """Return the PDF-ready Markdown representation of the assembled report."""
        return analysis.markdown_report


def build_quality_section(analysis: ReviewAnalysis) -> dict[str, Any]:
    """Convert the quality analysis into report section data."""
    return {
        "score": analysis.quality_score,
        "summary": analysis.summary,
        "suggestions": analysis.suggestions,
    }


def build_security_section(analysis: SecurityAnalysis) -> dict[str, Any]:
    """Convert the security analysis into report section data."""
    return {
        "score": score_security(analysis),
        "summary": analysis.summary,
        "overall_severity": analysis.overall_severity,
        "findings": [finding.__dict__ for finding in analysis.findings],
    }


def build_performance_section(analysis: PerformanceAnalysis) -> dict[str, Any]:
    """Convert the performance analysis into report section data."""
    return {
        "score": score_performance(analysis),
        "summary": analysis.summary,
        "time_complexity": analysis.time_complexity,
        "space_complexity": analysis.space_complexity,
        "memory_usage": analysis.memory_usage,
        "inefficient_loops": analysis.inefficient_loops,
        "duplicate_work": analysis.duplicate_work,
        "better_algorithms": analysis.better_algorithms,
    }


def build_refactoring_section(analysis: RefactoringAnalysis) -> dict[str, Any]:
    """Convert the refactoring analysis into report section data."""
    return {
        "score": score_refactoring(analysis),
        "summary": analysis.summary,
        "changes": analysis.changes,
        "improved_code": analysis.improved_code,
    }


def build_tests_section(analysis: UnitTestGenerationAnalysis) -> dict[str, Any]:
    """Convert the unit test generation analysis into report section data."""
    return {
        "score": score_tests(analysis),
        "summary": analysis.summary,
        "test_code": analysis.test_code,
    }


def build_documentation_section(analysis: DocumentationAnalysis) -> dict[str, Any]:
    """Convert the documentation analysis into report section data."""
    return {
        "score": score_documentation(analysis),
        "summary": analysis.summary,
        "markdown_documentation": analysis.markdown_documentation,
    }


def calculate_overall_score(*scores: int) -> int:
    """Calculate a weighted-friendly overall score from section scores."""
    if not scores:
        return 0
    return max(0, min(100, round(sum(scores) / len(scores))))


def score_security(analysis: SecurityAnalysis) -> int:
    """Score security posture based on the highest severity and finding count."""
    if not analysis.findings:
        return 100
    severity_score = {"Low": 90, "Medium": 70, "High": 45, "Critical": 15}
    worst = min(severity_score.get(finding.severity, 70) for finding in analysis.findings)
    penalty = min(20, max(0, len(analysis.findings) - 1) * 5)
    return max(0, worst - penalty)


def score_performance(analysis: PerformanceAnalysis) -> int:
    """Score performance based on complexity and inefficiency signals."""
    base = complexity_score(analysis.time_complexity)
    penalty = len(analysis.inefficient_loops) * 15 + len(analysis.duplicate_work) * 10
    return max(0, base - penalty)


def score_refactoring(analysis: RefactoringAnalysis) -> int:
    """Score refactoring based on how much improvement was suggested."""
    if not analysis.changes:
        return 100
    return max(50, 90 - len(analysis.changes) * 5)


def score_tests(analysis: UnitTestGenerationAnalysis) -> int:
    """Score test generation based on test richness and executable coverage hints."""
    if not analysis.test_code.strip():
        return 0
    test_count = analysis.test_code.count("def test_")
    bonus = 0
    if "pytest.raises" in analysis.test_code:
        bonus += 15
    if "parametrize" in analysis.test_code:
        bonus += 10
    return min(100, 60 + test_count * 5 + bonus)


def score_documentation(analysis: DocumentationAnalysis) -> int:
    """Score documentation quality based on required Markdown sections."""
    if not analysis.markdown_documentation.strip():
        return 0
    if documentation_has_required_sections(analysis.markdown_documentation):
        return 100
    section_count = sum(
        1
        for heading in (
            "# Overview",
            "# Purpose",
            "# Function Descriptions",
            "# Inputs",
            "# Outputs",
            "# Usage Examples",
        )
        if heading.lower() in analysis.markdown_documentation.lower()
    )
    return min(100, section_count * 15 + 10)


def complexity_score(time_complexity: str) -> int:
    """Map a time-complexity label to a rough quality score."""
    text = time_complexity.lower().replace(" ", "")
    if "o(1)" in text:
        return 100
    if "o(logn)" in text:
        return 92
    if "o(n)" in text and "o(n^2)" not in text and "o(n3)" not in text:
        return 85
    if "o(nlogn)" in text:
        return 88
    if "o(n^2)" in text or "o(n*n)" in text:
        return 55
    if "o(n^3)" in text:
        return 30
    return 70


def build_executive_summary(
    quality_section: dict[str, Any],
    security_section: dict[str, Any],
    performance_section: dict[str, Any],
    refactoring_section: dict[str, Any],
    tests_section: dict[str, Any],
    documentation_section: dict[str, Any],
    overall_score: int,
) -> str:
    """Build a concise executive summary across all generated sections."""
    return (
        f"Overall score {overall_score}/100. "
        f"Quality scored {quality_section['score']}, security {security_section['score']}, "
        f"performance {performance_section['score']}, refactoring {refactoring_section['score']}, "
        f"tests {tests_section['score']}, and documentation {documentation_section['score']}."
    )


def render_markdown_report(
    *,
    file_name: str,
    executive_summary: str,
    quality_section: dict[str, Any],
    security_section: dict[str, Any],
    performance_section: dict[str, Any],
    refactoring_section: dict[str, Any],
    tests_section: dict[str, Any],
    documentation_section: dict[str, Any],
    overall_score: int,
    review_context: str,
) -> str:
    """Render a PDF-ready Markdown report from the aggregated analysis data."""
    findings_lines = "\n".join(f"- {finding['issue']} ({finding['severity']})" for finding in security_section["findings"]) or "- None"
    quality_suggestions = "\n".join(f"- {item}" for item in quality_section["suggestions"]) or "- None"
    performance_loops = "\n".join(f"- {item}" for item in performance_section["inefficient_loops"]) or "- None"
    duplicate_work = "\n".join(f"- {item}" for item in performance_section["duplicate_work"]) or "- None"
    better_algorithms = "\n".join(f"- {item}" for item in performance_section["better_algorithms"]) or "- None"
    refactoring_changes = "\n".join(f"- {item}" for item in refactoring_section["changes"]) or "- None"
    test_preview = tests_section["test_code"].strip() or "No test code generated."
    documentation_preview = documentation_section["markdown_documentation"].strip() or "No documentation generated."

    return (
        f"# Executive Summary\n\n"
        f"{executive_summary}\n\n"
        f"# Quality\n\n"
        f"Score: {quality_section['score']}/100\n\n"
        f"{quality_section['summary']}\n\n"
        f"## Suggestions\n\n{quality_suggestions}\n\n"
        f"# Security\n\n"
        f"Score: {security_section['score']}/100\n\n"
        f"Severity: {security_section['overall_severity']}\n\n"
        f"{security_section['summary']}\n\n"
        f"## Findings\n\n{findings_lines}\n\n"
        f"# Performance\n\n"
        f"Score: {performance_section['score']}/100\n\n"
        f"{performance_section['summary']}\n\n"
        f"- Time Complexity: {performance_section['time_complexity']}\n"
        f"- Space Complexity: {performance_section['space_complexity']}\n"
        f"- Memory Usage: {performance_section['memory_usage']}\n\n"
        f"## Inefficient Loops\n\n{performance_loops}\n\n"
        f"## Duplicate Work\n\n{duplicate_work}\n\n"
        f"## Better Algorithms\n\n{better_algorithms}\n\n"
        f"# Refactoring\n\n"
        f"Score: {refactoring_section['score']}/100\n\n"
        f"{refactoring_section['summary']}\n\n"
        f"## Changes\n\n{refactoring_changes}\n\n"
        f"## Improved Code\n\n```text\n{refactoring_section['improved_code'].strip()}\n```\n\n"
        f"# Tests\n\n"
        f"Score: {tests_section['score']}/100\n\n"
        f"{tests_section['summary']}\n\n"
        f"## Executable Pytest Code\n\n```python\n{test_preview}\n```\n\n"
        f"# Documentation\n\n"
        f"Score: {documentation_section['score']}/100\n\n"
        f"{documentation_section['summary']}\n\n"
        f"## Markdown Documentation\n\n{documentation_preview}\n\n"
        f"# Overall Score\n\n"
        f"{overall_score}/100\n\n"
        f"_File_: {file_name}\n\n"
        f"_Review context_: {review_context or 'No additional context provided.'}\n"
    ).strip()