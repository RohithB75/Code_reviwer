from fastapi import APIRouter, Depends

from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.core.llm_factory import build_llm_service
from app.schemas.documentation import DocumentationGenerationRequest, DocumentationGenerationResponse

router = APIRouter(prefix="/documentation", tags=["documentation"])


def get_review_engine(settings: Settings = Depends(get_settings)) -> ReviewEngine:
    llm_service = build_llm_service(
        settings,
        provider=settings.documentation_llm_provider or "groq",
        fallback_provider=settings.documentation_llm_fallback_provider or "ollama",
    )
    return ReviewEngine(llm_service=llm_service)


@router.post("/generate", response_model=DocumentationGenerationResponse, summary="Generate markdown documentation")
async def generate_documentation(
    payload: DocumentationGenerationRequest,
    review_engine: ReviewEngine = Depends(get_review_engine),
) -> DocumentationGenerationResponse:
    analysis = review_engine.generate_documentation(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    return DocumentationGenerationResponse(
        language=analysis.language,
        summary=analysis.summary,
        markdown_documentation=analysis.markdown_documentation,
    )