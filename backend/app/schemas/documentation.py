from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentationGenerationRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    source_code: str = Field(min_length=1, description="Source code to document")
    file_name: str | None = Field(default=None, description="Optional source file name")
    review_context: str = Field(default="", description="Optional documentation context or constraints")
    language_hint: str | None = Field(default=None, description="Optional language hint")


class DocumentationGenerationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    language: str
    summary: str
    markdown_documentation: str
