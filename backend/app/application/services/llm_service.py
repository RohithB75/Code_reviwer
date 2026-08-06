from __future__ import annotations

import logging
from typing import Any, Protocol

from app.infrastructure.groq_client import GroqClientError
from app.infrastructure.ollama_client import OllamaClient, OllamaClientError, OllamaCompletion

logger = logging.getLogger(__name__)

# Errors from either backend that indicate the *provider* failed (timed out,
# unreachable, bad response) rather than the request itself being invalid.
# These are the cases worth retrying against a fallback provider.
RETRYABLE_LLM_ERRORS: tuple[type[Exception], ...] = (OllamaClientError, GroqClientError)


class Completion(Protocol):
    model: str
    prompt: str
    response: str
    base_url: str


class LLMService:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    def generate_text(
        self,
        prompt: str,
        *,
        structured: bool = False,
        options: dict[str, Any] | None = None,
    ) -> OllamaCompletion:
        return self.client.generate_text(prompt, format_json=structured, options=options)

    def test_prompt(self, prompt: str) -> OllamaCompletion:
        return self.generate_text(prompt)


class FallbackLLMService:
    """Wraps a primary LLMService and one or more fallback LLMServices.
    If the primary provider raises a retryable error (timeout, connection
    failure, bad/empty response), each fallback is tried in order before
    giving up. This lets a fast local model (Ollama) handle most requests
    while a stronger hosted model (e.g. Groq) only gets used - and billed/
    rate-limited - when it's actually needed.
    """

    def __init__(self, primary: LLMService, fallbacks: list[LLMService]) -> None:
        self.primary = primary
        self.fallbacks = fallbacks

    def generate_text(
        self,
        prompt: str,
        *,
        structured: bool = False,
        options: dict[str, Any] | None = None,
    ) -> Completion:
        services = [self.primary, *self.fallbacks]
        last_error: Exception | None = None

        for index, service in enumerate(services):
            try:
                completion = service.generate_text(prompt, structured=structured, options=options)
            except RETRYABLE_LLM_ERRORS as exc:
                last_error = exc
                provider_name = type(service.client).__name__
                if index + 1 < len(services):
                    next_provider = type(services[index + 1].client).__name__
                    logger.warning(
                        "%s failed (%s); falling back to %s.",
                        provider_name,
                        exc,
                        next_provider,
                    )
                    continue
                logger.error("%s failed and no further fallbacks are configured: %s", provider_name, exc)
                raise
            else:
                if index > 0:
                    logger.info("Fallback provider %s succeeded.", type(service.client).__name__)
                return completion

        # Unreachable in practice (loop either returns or raises), but keeps
        # type-checkers happy and fails loudly if it ever is reached.
        assert last_error is not None
        raise last_error

    def test_prompt(self, prompt: str) -> Completion:
        return self.generate_text(prompt)