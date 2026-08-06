from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


class GroqClientError(RuntimeError):
    """Base error for Groq client failures."""


class GroqConnectionError(GroqClientError):
    """Raised when the Groq API cannot be reached."""


class GroqTimeoutError(GroqClientError):
    """Raised when a Groq request times out."""


class GroqResponseError(GroqClientError):
    """Raised when Groq returns an unexpected response."""


class GroqAuthError(GroqClientError):
    """Raised when the Groq API key is missing or invalid."""


@dataclass(frozen=True)
class GroqCompletion:
    """Mirrors app.infrastructure.ollama_client.OllamaCompletion so
    LLMService can use either backend interchangeably."""

    model: str
    prompt: str
    response: str
    base_url: str


class GroqClient:
    """Client for Groq's OpenAI-compatible chat completions API.
    https://console.groq.com/docs/api-reference#chat-create
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        timeout_seconds: float,
        base_url: str = "https://api.groq.com/openai/v1/",
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds
        self.base_url = base_url.rstrip("/") + "/"

    def build_generate_payload(
        self,
        prompt: str,
        *,
        format_json: bool = False,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if format_json:
            payload["response_format"] = {"type": "json_object"}
        if options:
            # Map the same option names used for Ollama onto Groq/OpenAI
            # equivalents where they exist; unmapped keys are ignored.
            if "num_predict" in options:
                payload["max_tokens"] = options["num_predict"]
            if "temperature" in options:
                payload["temperature"] = options["temperature"]
        return payload

    def generate_text(
        self,
        prompt: str,
        *,
        format_json: bool = False,
        options: dict[str, Any] | None = None,
    ) -> GroqCompletion:
        if not self.api_key:
            raise GroqAuthError(
                "GROQ_API_KEY is not set. Add it to your .env file to use the Groq provider."
            )

        url = urljoin(self.base_url, "chat/completions")
        payload = self.build_generate_payload(prompt, format_json=format_json, options=options)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise GroqTimeoutError(
                f"Groq request timed out after {self.timeout_seconds} seconds."
            ) from exc
        except requests.ConnectionError as exc:
            raise GroqConnectionError("Unable to connect to the Groq API.") from exc
        except requests.HTTPError as exc:
            if exc.response is not None and exc.response.status_code in (401, 403):
                raise GroqAuthError(
                    "Groq rejected the request: check that GROQ_API_KEY is valid."
                ) from exc
            raise GroqResponseError(self._extract_error_message(exc.response)) from exc
        except requests.RequestException as exc:
            raise GroqClientError(f"Groq request failed: {exc}") from exc

        data = self._parse_response_json(response)
        try:
            content = str(data["choices"][0]["message"]["content"]).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise GroqResponseError("Groq returned an unexpected response payload.") from exc

        return GroqCompletion(
            model=data.get("model", self.model),
            prompt=prompt,
            response=content,
            base_url=self.base_url.rstrip("/"),
        )

    @staticmethod
    def _parse_response_json(response: requests.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise GroqResponseError("Groq returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise GroqResponseError("Groq returned an unexpected response payload.")
        return payload

    @staticmethod
    def _extract_error_message(response: requests.Response | None) -> str:
        if response is None:
            return "Groq returned an unknown error."
        try:
            payload = response.json()
        except ValueError:
            return response.text or f"Groq request failed with HTTP {response.status_code}."

        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, dict):
                return str(error.get("message") or f"HTTP {response.status_code}")
            return str(payload.get("message") or f"HTTP {response.status_code}")
        return f"Groq request failed with HTTP {response.status_code}."