from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ReportOutputFormat = Literal["json", "markdown", "both"]


class ReportRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_code: str = Field(min_length=1, description="Source code to analyze for the report")
    file_name: str | None = Field(default=None, description="Optional source file name")
    review_context: str = Field(default="", description="Optional report context or constraints")
    language_hint: str | None = Field(default=None, description="Optional language hint")
    output_format: ReportOutputFormat = Field(default="both", description="Preferred report format")


class ReportQualitySection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    suggestions: list[str]


class ReportSecuritySection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    overall_severity: str
    findings: list[dict[str, Any]]


class ReportPerformanceSection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    time_complexity: str
    space_complexity: str
    memory_usage: str
    inefficient_loops: list[str]
    duplicate_work: list[str]
    better_algorithms: list[str]


class ReportRefactoringSection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    changes: list[str]
    improved_code: str


class ReportTestsSection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    test_code: str


class ReportDocumentationSection(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    score: int
    summary: str
    markdown_documentation: str


class ReportPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    executive_summary: str
    quality: ReportQualitySection
    security: ReportSecuritySection
    performance: ReportPerformanceSection
    refactoring: ReportRefactoringSection
    tests: ReportTestsSection
    documentation: ReportDocumentationSection
    overall_score: int


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    format: ReportOutputFormat
    pdf_export_ready: bool
    report: ReportPayload | str
    markdown_report: str
    json_report: dict[str, Any]
    export_metadata: ReportExportMetadata


class ReportExportMetadata(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    pdf_export_ready: bool
    markdown_report: str
    json_report: dict[str, Any]
