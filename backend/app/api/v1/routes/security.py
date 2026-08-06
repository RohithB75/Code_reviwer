from fastapi import APIRouter, Depends

from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.core.llm_factory import build_llm_service
from app.schemas.security import SecurityReviewRequest, SecurityReviewResponse

router = APIRouter(prefix="/security", tags=["security"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    llm_service = build_llm_service(settings)
    return ReviewEngine(llm_service=llm_service)


@router.post("/analyze", response_model=SecurityReviewResponse, summary="Run a structured security review")
async def analyze_security_code(
    payload: SecurityReviewRequest,
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> SecurityReviewResponse:
    analysis = review_engine.security_review_source_code(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return SecurityReviewResponse(
        language=analysis.language,
        summary=analysis.summary,
        overall_severity=analysis.overall_severity,
        findings=analysis.findings,
    )