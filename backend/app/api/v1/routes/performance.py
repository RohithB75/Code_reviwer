from fastapi import APIRouter, Depends

from app.application.services.llm_service import LLMService
from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.infrastructure.ollama_client import OllamaClient
from app.schemas.performance import PerformanceAnalysisRequest, PerformanceAnalysisResponse

router = APIRouter(prefix="/performance", tags=["performance"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    llm_service = LLMService(client)
    return ReviewEngine(llm_service=llm_service)


@router.post("/analyze", response_model=PerformanceAnalysisResponse, summary="Run a structured performance analysis")
async def analyze_performance_code(
    payload: PerformanceAnalysisRequest,
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> PerformanceAnalysisResponse:
    analysis = review_engine.performance_analysis_source_code(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return PerformanceAnalysisResponse(
        language=analysis.language,
        summary=analysis.summary,
        time_complexity=analysis.time_complexity,
        space_complexity=analysis.space_complexity,
        memory_usage=analysis.memory_usage,
        inefficient_loops=analysis.inefficient_loops,
        duplicate_work=analysis.duplicate_work,
        better_algorithms=analysis.better_algorithms,
    )
