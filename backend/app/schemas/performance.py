from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PerformanceAnalysisRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_code: str = Field(min_length=1, description="Source code to analyze")
    file_name: str | None = Field(default=None, description="Optional source file name")
    review_context: str = Field(default="", description="Optional review context or instructions")
    language_hint: str | None = Field(default=None, description="Optional language hint")


class PerformanceAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: str
    summary: str
    time_complexity: str
    space_complexity: str
    memory_usage: str
    inefficient_loops: list[str]
    duplicate_work: list[str]
    better_algorithms: list[str]
