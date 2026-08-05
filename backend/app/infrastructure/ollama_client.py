from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


class OllamaClientError(RuntimeError):
    """Base error for Ollama client failures."""


class OllamaConnectionError(OllamaClientError):
    """Raised when the Ollama server cannot be reached."""


class OllamaTimeoutError(OllamaClientError):
    """Raised when an Ollama request times out."""


class OllamaResponseError(OllamaClientError):
    """Raised when Ollama returns an unexpected response."""


@dataclass(frozen=True)
class OllamaCompletion:
    model: str
    prompt: str
    response: str
    base_url: str


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.model = model
        self.timeout_seconds = timeout_seconds

    def build_generate_payload(
        self,
        prompt: str,
        *,
        format_json: bool = False,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if format_json:
            payload["format"] = "json"
        if options:
            payload["options"] = options
        return payload

    def generate_text(
        self,
        prompt: str,
        *,
        format_json: bool = False,
        options: dict[str, Any] | None = None,
    ) -> OllamaCompletion:
        url = urljoin(self.base_url, "api/generate")
        payload = self.build_generate_payload(prompt, format_json=format_json, options=options)
        clean_base_url = self.base_url.rstrip("/")

        try:
            response = requests.post(url, json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
        except requests.Timeout as exc:
            raise OllamaTimeoutError(
                f"Ollama request timed out after {self.timeout_seconds} seconds."
            ) from exc
        except requests.ConnectionError as exc:
            raise OllamaConnectionError(f"Unable to connect to Ollama at {clean_base_url}.") from exc
        except requests.HTTPError as exc:
            raise OllamaResponseError(self._extract_error_message(exc.response)) from exc
        except requests.RequestException as exc:
            raise OllamaClientError(f"Ollama request failed: {exc}") from exc

        data = self._parse_response_json(response)
        return OllamaCompletion(
            model=data.get("model", self.model),
            prompt=prompt,
            response=str(data.get("response", "")).strip(),
            base_url=clean_base_url,
        )

    @staticmethod
    def _parse_response_json(response: requests.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise OllamaResponseError("Ollama returned invalid JSON.") from exc

        if not isinstance(payload, dict):
            raise OllamaResponseError("Ollama returned an unexpected response payload.")
        return payload

    @staticmethod
    def _extract_error_message(response: requests.Response | None) -> str:
        if response is None:
            return "Ollama returned an unknown error."
        try:
            payload = response.json()
        except ValueError:
            return response.text or f"Ollama request failed with HTTP {response.status_code}."

        if isinstance(payload, dict):
            return str(payload.get("error") or payload.get("message") or f"HTTP {response.status_code}")
        return f"Ollama request failed with HTTP {response.status_code}."