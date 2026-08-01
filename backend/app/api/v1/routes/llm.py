from fastapi import APIRouter, Depends

from app.application.services.llm_service import LLMService
from app.core.config import Settings, get_settings
from app.infrastructure.ollama_client import (
    OllamaClient,
    OllamaConnectionError,
    OllamaTimeoutError,
)
from app.schemas.llm import LLMTestRequest, LLMTestResponse

router = APIRouter(prefix="/llm", tags=["llm"])


def get_llm_service(settings: Settings = Depends(get_settings)) -> LLMService:
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    return LLMService(client)


@router.post("/test", response_model=LLMTestResponse, summary="Run a simple Ollama prompt")
async def test_llm_prompt(payload: LLMTestRequest, llm_service: LLMService = Depends(get_llm_service)) -> LLMTestResponse:
    completion = llm_service.test_prompt(payload.prompt)
    return LLMTestResponse(
        model=completion.model,
        prompt=completion.prompt,
        response=completion.response,
        base_url=completion.base_url,
    )