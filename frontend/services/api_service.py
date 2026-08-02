from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests


@dataclass(frozen=True)
class ApiResponse:
    ok: bool
    status_code: int | None
    data: dict[str, Any] | None = None
    error: str | None = None


class ApiService:
    def __init__(self, base_url: str, timeout_seconds: float = 8.0) -> None:
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> ApiResponse:
        url = urljoin(self.base_url, "api/v1/health")
        try:
            response = requests.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
            return ApiResponse(ok=True, status_code=response.status_code, data=response.json())
        except requests.HTTPError as exc:
            response = exc.response
            message = self._extract_error_message(response)
            return ApiResponse(ok=False, status_code=response.status_code if response is not None else None, error=message)
        except requests.RequestException as exc:
            return ApiResponse(ok=False, status_code=None, error=str(exc))
        except ValueError as exc:
            return ApiResponse(ok=False, status_code=None, error=f"Invalid JSON response: {exc}")

    def analyze_review(
        self,
        *,
        source_code: str,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> ApiResponse:
        """Calls POST /api/v1/review/analyze with the code + review context
        and returns the LLM-generated review (language, summary, suggestions,
        quality_score)."""
        payload = {
            "source_code": source_code,
            "file_name": file_name,
            "review_context": review_context,
            "language_hint": language_hint,
        }
        return self._post("api/v1/review/analyze", payload, timeout_seconds=90.0)

    def _post(self, path: str, payload: dict[str, Any], *, timeout_seconds: float | None = None) -> ApiResponse:
        url = urljoin(self.base_url, path)
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=timeout_seconds or self.timeout_seconds,
            )
            response.raise_for_status()
            return ApiResponse(ok=True, status_code=response.status_code, data=response.json())
        except requests.HTTPError as exc:
            response = exc.response
            message = self._extract_error_message(response)
            return ApiResponse(ok=False, status_code=response.status_code if response is not None else None, error=message)
        except requests.RequestException as exc:
            return ApiResponse(ok=False, status_code=None, error=str(exc))
        except ValueError as exc:
            return ApiResponse(ok=False, status_code=None, error=f"Invalid JSON response: {exc}")

    @staticmethod
    def _extract_error_message(response: requests.Response | None) -> str:
        if response is None:
            return "Backend request failed without a response."
        try:
            payload = response.json()
        except ValueError:
            return response.text or f"HTTP {response.status_code}"

        if isinstance(payload, dict):
            return str(payload.get("message") or payload.get("detail") or f"HTTP {response.status_code}")
        return f"HTTP {response.status_code}"