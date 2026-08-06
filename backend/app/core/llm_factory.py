from __future__ import annotations

from app.application.services.llm_service import FallbackLLMService, LLMService
from app.core.config import Settings
from app.infrastructure.groq_client import GroqClient
from app.infrastructure.ollama_client import OllamaClient


def _build_single_provider_service(provider: str, settings: Settings) -> LLMService:
    provider = provider.strip().lower()

    if provider == "groq":
        client = GroqClient(
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            timeout_seconds=settings.groq_timeout_seconds,
        )
        return LLMService(client)

    # Default: ollama
    client = OllamaClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        timeout_seconds=settings.ollama_timeout_seconds,
    )
    return LLMService(client)


def build_llm_service(
    settings: Settings,
    *,
    provider: str | None = None,
    fallback_provider: str | None = None,
) -> LLMService | FallbackLLMService:
    """Build the LLM service used by ReviewEngine, based on settings/.env:

    - LLM_PROVIDER ("ollama" or "groq", default "ollama") selects the
      global default primary provider.
    - LLM_FALLBACK_PROVIDER (optional) selects a provider to retry with if
      the primary fails (timeout, connection error, bad response). Typical
      setup: LLM_PROVIDER=ollama (fast, free, local) with
      LLM_FALLBACK_PROVIDER=groq (stronger, hosted) so Groq is only used
      when the local model actually fails or can't be reached.

    A caller can override the provider/fallback_provider for a specific
    task (e.g. documentation generation, which needs a bigger context
    window and more reliable instruction-following than a small local
    model provides) by passing `provider=`/`fallback_provider=` explicitly
    - typically sourced from a task-specific setting such as
    DOCUMENTATION_LLM_PROVIDER, falling back to the global setting when
    that's blank.

    Both clients expose the same generate_text(prompt, format_json=...,
    options=...) interface, so ReviewEngine doesn't need to know which
    provider(s) are in use.
    """
    effective_provider = (provider or settings.llm_provider).strip().lower()
    effective_fallback = (fallback_provider or settings.llm_fallback_provider).strip().lower()

    primary = _build_single_provider_service(effective_provider, settings)

    if not effective_fallback or effective_fallback == effective_provider:
        return primary

    fallback = _build_single_provider_service(effective_fallback, settings)
    return FallbackLLMService(primary=primary, fallbacks=[fallback])