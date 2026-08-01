from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EchoRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str = Field(min_length=1, max_length=200)
    tags: list[str] = Field(default_factory=list)


class EchoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message: str
    tags: list[str]
    tag_count: int