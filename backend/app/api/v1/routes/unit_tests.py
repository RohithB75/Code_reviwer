from fastapi import APIRouter, Depends

from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.core.llm_factory import build_llm_service
from app.schemas.unit_tests import UnitTestGenerationRequest, UnitTestGenerationResponse

router = APIRouter(prefix="/unit-tests", tags=["unit-tests"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    llm_service = build_llm_service(settings)
    return ReviewEngine(llm_service=llm_service)


@router.post("/generate", response_model=UnitTestGenerationResponse, summary="Generate executable pytest tests")
async def generate_unit_tests(
    payload: UnitTestGenerationRequest,
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> UnitTestGenerationResponse:
    analysis = review_engine.generate_unit_tests(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return UnitTestGenerationResponse(
        language=analysis.language,
        summary=analysis.summary,
        test_code=analysis.test_code,
    )