from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LLMTestRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prompt: str = Field(default="Say hello in one short sentence.", min_length=1, max_length=500)


class LLMTestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model: str
    prompt: str
    response: str
    base_url: str
