from __future__ import annotations

from typing import Any

from app.infrastructure.ollama_client import OllamaClient, OllamaCompletion


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