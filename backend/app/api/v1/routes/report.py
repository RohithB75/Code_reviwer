from fastapi import APIRouter, Depends

from app.application.services.llm_service import LLMService
from app.application.services.report_engine import ReportEngine
from app.application.services.review_engine import ReviewEngine
from app.core.config import Settings, get_settings
from app.infrastructure.ollama_client import OllamaClient
from app.schemas.report import ReportPayload, ReportRequest, ReportResponse

router = APIRouter(prefix="/report", tags=["report"])


def get_report_engine(settings: Settings = Depends(get_settings)) -> ReportEngine:
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    llm_service = LLMService(client)
    review_engine = ReviewEngine(llm_service=llm_service)
    return ReportEngine(review_engine=review_engine)


@router.post("/generate", response_model=ReportResponse, summary="Generate a combined code review report")
async def generate_report(
    payload: ReportRequest,
    report_engine: ReportEngine = Depends(get_report_engine),
) -> ReportResponse:
    analysis = report_engine.generate_report(
        payload.source_code,
        file_name=payload.file_name,
        review_context=payload.review_context,
        language_hint=payload.language_hint,
    )
    report_payload = report_engine.build_report_payload(analysis)
    markdown_report = report_engine.build_report_markdown(analysis)
    export_metadata = report_engine.build_report_export_metadata(analysis)
    report_model = ReportPayload(**report_payload)

    if payload.output_format == "json":
        report_value: ReportPayload | str = report_model
    elif payload.output_format == "markdown":
        report_value = markdown_report
    else:
        report_value = report_model

    return ReportResponse(
        format=payload.output_format,
        pdf_export_ready=export_metadata.pdf_export_ready,
        report=report_value,
        markdown_report=markdown_report,
        json_report=report_payload,
        export_metadata=export_metadata,
    )
