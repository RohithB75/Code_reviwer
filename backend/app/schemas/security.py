from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SecurityReviewRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_code: str = Field(min_length=1, description="Source code to security review")
    file_name: str | None = Field(default=None, description="Optional source file name")
    review_context: str = Field(default="", description="Optional review context or instructions")
    language_hint: str | None = Field(default=None, description="Optional language hint")


class SecurityFinding(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    issue: str
    severity: str
    description: str
    evidence: str
    recommendation: str


class SecurityReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: str
    summary: str
    overall_severity: str
    findings: list[SecurityFinding]
