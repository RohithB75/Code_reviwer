from fastapi import APIRouter, Depends

from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.core.llm_factory import build_llm_service
from app.schemas.review import ReviewRequest, ReviewResponse

router = APIRouter(prefix="/review", tags=["review"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    llm_service = build_llm_service(settings)
    return ReviewEngine(llm_service=llm_service)


@router.post("/analyze", response_model=ReviewResponse, summary="Analyze source code and return structured review output")
async def analyze_source_code(payload: ReviewRequest, review_engine: ReviewEngine = Depends(get_review_engine)) -> ReviewResponse:
    analysis = review_engine.review_source_code(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return ReviewResponse(
        language=analysis.language,
        summary=analysis.summary,
        suggestions=analysis.suggestions,
        quality_score=analysis.quality_score,
    )