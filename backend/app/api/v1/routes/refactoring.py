from fastapi import APIRouter, Depends

from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.core.llm_factory import build_llm_service
from app.schemas.refactoring import RefactoringRequest, RefactoringResponse

router = APIRouter(prefix="/refactoring", tags=["refactoring"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    llm_service = build_llm_service(settings)
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