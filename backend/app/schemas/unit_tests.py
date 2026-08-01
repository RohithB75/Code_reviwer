from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class UnitTestGenerationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_code: str = Field(min_length=1, description="Source code to generate tests for")
    file_name: str | None = Field(default=None, description="Optional source file name")
    review_context: str = Field(default="", description="Optional test generation context or constraints")
    language_hint: str | None = Field(default=None, description="Optional language hint")


class UnitTestGenerationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: str
    summary: str
    test_code: str
