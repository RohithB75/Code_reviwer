from __future__ import annotations

from app.infrastructure.ollama_client import OllamaClient, OllamaCompletion


class LLMService:
    def __init__(self, client: OllamaClient) -> None:
        self.client = client

    def generate_text(self, prompt: str, *, structured: bool = False) -> OllamaCompletion:
        return self.client.generate_text(prompt, format_json=structured)

    def test_prompt(self, prompt: str) -> OllamaCompletion:
        return self.generate_text(prompt)
