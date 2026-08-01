from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ServiceInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    environment: str
    version: str
    api_prefix: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    error: str
    message: str
    details: list[dict[str, Any]] | None = Field(default=None)