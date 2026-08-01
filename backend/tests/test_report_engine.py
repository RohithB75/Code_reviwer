from __future__ import annotations

from app.application.services.report_engine import ReportEngine
from app.application.services.review_engine import (
    ReviewAnalysis,
    SecurityAnalysis,
    PerformanceAnalysis,
    RefactoringAnalysis,
    UnitTestGenerationAnalysis,
    DocumentationAnalysis,
)


class FakeReviewEngine:
    def review_source_code(self, *args, **kwargs) -> ReviewAnalysis:
        return ReviewAnalysis(language="Python", summary="OK", suggestions=["s1"], quality_score=80)

    def security_review_source_code(self, *args, **kwargs) -> SecurityAnalysis:
        return SecurityAnalysis(language="Python", summary="Safe", overall_severity="Low", findings=[])

    def performance_analysis_source_code(self, *args, **kwargs) -> PerformanceAnalysis:
        return PerformanceAnalysis(
            language="Python",
            summary="Fast",
            time_complexity="O(1)",
            space_complexity="O(1)",
            memory_usage="low",
            inefficient_loops=[],
            duplicate_work=[],
            better_algorithms=[],
        )

    def refactor_source_code(self, *args, **kwargs) -> RefactoringAnalysis:
        return RefactoringAnalysis(language="Python", summary="Fine", changes=["c1"], improved_code="def add(a,b): return a+b")

    def generate_unit_tests(self, *args, **kwargs) -> UnitTestGenerationAnalysis:
        return UnitTestGenerationAnalysis(language="Python", summary="Tests", test_code="def test_add(): assert True")

    def generate_documentation(self, *args, **kwargs) -> DocumentationAnalysis:
        return DocumentationAnalysis(language="Python", summary="Docs", markdown_documentation="# Overview\n")


def test_report_engine_generates_payload_and_markdown():
    fake = FakeReviewEngine()
    engine = ReportEngine(review_engine=fake)

    analysis = engine.generate_report("def add(a,b): return a+b", file_name="example.py", review_context="ctx")

    payload = engine.build_report_payload(analysis)
    md = engine.build_report_markdown(analysis)
    export_meta = engine.build_report_export_metadata(analysis)

    assert "executive_summary" in payload
    assert payload["overall_score"] >= 0
    assert isinstance(md, str) and md.strip() != ""
    assert export_meta.pdf_export_ready is True
    assert export_meta.json_report["executive_summary"] == payload["executive_summary"]
