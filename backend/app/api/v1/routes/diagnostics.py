from fastapi import APIRouter

from app.schemas.diagnostics import EchoRequest, EchoResponse

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])


@router.post("/echo", response_model=EchoResponse, summary="Validate and echo a diagnostic payload")
async def echo(payload: EchoRequest) -> EchoResponse:
    normalized_message = payload.message.strip()
    return EchoResponse(
        message=normalized_message,
        tags=payload.tags,
        tag_count=len(payload.tags),
    )