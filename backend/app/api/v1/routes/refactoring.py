from fastapi import APIRouter, Depends

from app.application.services.llm_service import LLMService
from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.infrastructure.ollama_client import OllamaClient
from app.schemas.refactoring import RefactoringRequest, RefactoringResponse

router = APIRouter(prefix="/refactoring", tags=["refactoring"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    llm_service = LLMService(client)
    return ReviewEngine(llm_service=llm_service)


@router.post("/analyze", response_model=RefactoringResponse, summary="Refactor code and return improved source")
async def analyze_refactoring_code(
    payload: RefactoringRequest,
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> RefactoringResponse:
    analysis = review_engine.refactor_source_code(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return RefactoringResponse(
        language=analysis.language,
        summary=analysis.summary,
        changes=analysis.changes,
        improved_code=analysis.improved_code,
    )
