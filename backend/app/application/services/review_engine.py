from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.application.services.llm_service import LLMService
from app.prompts.manager import PromptManager

logger = logging.getLogger(__name__)


class ReviewEngineError(RuntimeError):
    """Base error for review engine failures."""


class ReviewParseError(ReviewEngineError):
    """Raised when the model response cannot be parsed into review JSON."""


@dataclass(frozen=True)
class ReviewAnalysis:
    language: str
    summary: str
    suggestions: list[str]
    quality_score: int


@dataclass(frozen=True)
class SecurityFindingAnalysis:
    issue: str
    severity: str
    description: str
    evidence: str
    recommendation: str


@dataclass(frozen=True)
class SecurityAnalysis:
    language: str
    summary: str
    overall_severity: str
    findings: list[SecurityFindingAnalysis]


@dataclass(frozen=True)
class PerformanceAnalysis:
    language: str
    summary: str
    time_complexity: str
    space_complexity: str
    memory_usage: str
    inefficient_loops: list[str]
    duplicate_work: list[str]
    better_algorithms: list[str]


@dataclass(frozen=True)
class RefactoringAnalysis:
    language: str
    summary: str
    changes: list[str]
    improved_code: str


@dataclass(frozen=True)
class UnitTestGenerationAnalysis:
    language: str
    summary: str
    test_code: str


@dataclass(frozen=True)
class DocumentationAnalysis:
    language: str
    summary: str
    markdown_documentation: str


REQUIRED_DOCUMENTATION_HEADINGS: tuple[str, ...] = (
    "# Overview",
    "# Language & Syntax Primer",
    "# Line-by-Line Walkthrough",
    "# Inputs",
    "# Outputs",
    "# Worked Example",
    "# Common Pitfalls",
    "# Usage Examples",
)


EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".java": "Java",
    ".rs": "Rust",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown",
}


class ReviewEngine:
    def __init__(self, llm_service: LLMService, prompt_manager: PromptManager | None = None) -> None:
        self.llm_service = llm_service
        self.prompt_manager = prompt_manager or PromptManager()

    def review_source_code(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> ReviewAnalysis:
        """Run the end-to-end review workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_review_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(prompt, structured=True)
        review_data = parse_review_payload(completion.response)
        return ReviewAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            suggestions=normalize_suggestions(review_data.get("suggestions", [])),
            quality_score=normalize_quality_score(review_data.get("quality_score", review_data.get("score", 0))),
        )

    def security_review_source_code(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> SecurityAnalysis:
        """Run the structured security review workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_security_review_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(prompt, structured=True)
        review_data = parse_review_payload(completion.response)
        findings = normalize_security_findings(review_data.get("findings", []))
        return SecurityAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            overall_severity=derive_overall_severity(
                findings,
                review_data.get("overall_severity", review_data.get("severity", "Low")),
            ),
            findings=findings,
        )

    def performance_analysis_source_code(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> PerformanceAnalysis:
        """Run the structured performance analysis workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_performance_review_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(prompt, structured=True)
        review_data = parse_review_payload(completion.response)
        return PerformanceAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            time_complexity=str(review_data.get("time_complexity", "Unknown")),
            space_complexity=str(review_data.get("space_complexity", "Unknown")),
            memory_usage=str(review_data.get("memory_usage", "")),
            inefficient_loops=normalize_suggestions(review_data.get("inefficient_loops", [])),
            duplicate_work=normalize_suggestions(review_data.get("duplicate_work", [])),
            better_algorithms=normalize_suggestions(review_data.get("better_algorithms", [])),
        )

    def refactor_source_code(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> RefactoringAnalysis:
        """Run the structured refactoring workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_refactoring_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(prompt, structured=True)
        review_data = parse_review_payload(completion.response)
        return RefactoringAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            changes=normalize_suggestions(review_data.get("changes", [])),
            improved_code=normalize_improved_code(review_data.get("improved_code", "")),
        )

    def generate_unit_tests(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> UnitTestGenerationAnalysis:
        """Run the structured unit test generation workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_unit_test_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(prompt, structured=True)
        review_data = parse_review_payload(completion.response)
        return UnitTestGenerationAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            test_code=normalize_test_code(review_data.get("test_code", review_data.get("tests", "")))
            or build_fallback_unit_test_code(source_code, file_name=file_name or "<unknown>"),
        )

    def generate_documentation(
        self,
        source_code: str,
        *,
        file_name: str | None = None,
        review_context: str = "",
        language_hint: str | None = None,
    ) -> DocumentationAnalysis:
        """Run the structured documentation generation workflow for a source snippet."""
        language = detect_language(source_code, file_name=file_name, language_hint=language_hint)
        prompt = build_documentation_prompt(
            prompt_manager=self.prompt_manager,
            source_code=source_code,
            language=language,
            file_name=file_name or "<unknown>",
            review_context=review_context,
        )
        completion = self.llm_service.generate_text(
            prompt,
            structured=True,
            options={"num_ctx": 8192, "num_predict": 4096},
        )
        review_data = parse_review_payload(completion.response)
        return DocumentationAnalysis(
            language=language,
            summary=str(review_data["summary"]),
            markdown_documentation=ensure_documentation_markdown(
                normalize_markdown_documentation(
                    review_data.get("markdown_documentation", review_data.get("documentation", ""))
                ),
                source_code=source_code,
                language=language,
                file_name=file_name or "<unknown>",
                review_context=review_context,
            ),
        )


def detect_language(source_code: str, *, file_name: str | None = None, language_hint: str | None = None) -> str:
    """Detect the source language using hints, filename, and code patterns."""
    if language_hint:
        return language_hint.strip() or "Unknown"

    if file_name:
        suffix = Path(file_name).suffix.lower()
        if suffix in EXTENSION_LANGUAGE_MAP:
            return EXTENSION_LANGUAGE_MAP[suffix]

    code_sample = source_code.lower()
    if "def " in code_sample and ":" in code_sample:
        return "Python"
    if "function " in code_sample or "=>" in code_sample:
        return "JavaScript"
    if "public class" in code_sample or "system.out" in code_sample:
        return "Java"
    if "package main" in code_sample:
        return "Go"
    if "fn " in code_sample and "->" in code_sample:
        return "Rust"
    if "<" in source_code and "/>" in source_code:
        return "TypeScript"
    return "Unknown"


def build_review_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the code review prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "code_review",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def build_security_review_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the security review prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "security_review",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def build_performance_review_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the performance review prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "performance_review",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def build_refactoring_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the refactoring prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "refactoring",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def build_unit_test_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the unit test generation prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "unit_tests",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def build_documentation_prompt(
    *,
    prompt_manager: PromptManager,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Render the documentation prompt template with the current review context."""
    return prompt_manager.get_prompt(
        "documentation",
        language=language,
        file_name=file_name,
        review_context=review_context or "No additional context provided.",
        code=source_code,
    )


def parse_review_payload(raw_response: str) -> dict[str, Any]:
    """Parse the LLM JSON payload into a Python dictionary."""
    candidate = raw_response.strip()
    if not candidate:
        raise ReviewParseError("Review response was empty.")

    json_text = extract_json_text(candidate)
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError:
        # Local/smaller models frequently emit literal newlines or unescaped
        # quotes inside JSON string values (e.g. multi-line markdown or code
        # embedded in a "markdown_documentation" field). Try a best-effort
        # repair before giving up, since re-prompting is expensive.
        try:
            payload = json.loads(repair_json_text(json_text))
        except json.JSONDecodeError as exc:
            logger.warning(
                "Failed to parse LLM response as JSON even after repair attempt. "
                "Raw response (first 4000 chars): %s",
                raw_response[:4000],
            )
            raise ReviewParseError("Review response was not valid JSON.") from exc

    if not isinstance(payload, dict):
        raise ReviewParseError("Review response JSON must be an object.")
    if "summary" not in payload:
        raise ReviewParseError("Review response is missing a summary field.")
    return payload


def repair_json_text(json_text: str) -> str:
    """Best-effort repair for common local-LLM JSON formatting mistakes:
    literal (unescaped) newlines/tabs inside string values, and stray
    backslashes that aren't valid JSON escape sequences (e.g. a model
    writing about code containing "\\d" or a Windows path without doubling
    the backslash for JSON). This walks the text character-by-character,
    tracking whether we are inside a JSON string, and repairs control
    characters and invalid escapes found there. It does not attempt to fix
    structurally broken/truncated JSON (unterminated strings, missing
    braces, etc.) — those are surfaced as a normal parse failure.
    """
    valid_escape_chars = set('"\\/bfnrtu')
    result: list[str] = []
    in_string = False
    i = 0
    length = len(json_text)
    while i < length:
        ch = json_text[i]
        if in_string:
            if ch == "\\":
                next_ch = json_text[i + 1] if i + 1 < length else ""
                if next_ch in valid_escape_chars:
                    result.append(ch)
                    result.append(next_ch)
                    i += 2
                    continue
                # Stray backslash (e.g. "\d", a Windows path, LaTeX, etc.)
                # that isn't a valid JSON escape — double it so it becomes
                # a literal backslash instead of breaking the parser.
                result.append("\\\\")
                i += 1
                continue
            if ch == '"':
                result.append(ch)
                in_string = False
                i += 1
                continue
            if ch == "\n":
                result.append("\\n")
                i += 1
                continue
            if ch == "\r":
                result.append("\\r")
                i += 1
                continue
            if ch == "\t":
                result.append("\\t")
                i += 1
                continue
            result.append(ch)
            i += 1
            continue
        # Not currently inside a string.
        if ch == '"':
            in_string = True
        result.append(ch)
        i += 1
    return "".join(result)


def extract_json_text(raw_text: str) -> str:
    """Extract a JSON object from model output, ignoring markdown fences when present."""
    fenced_match = re.search(r"```json\s*(\{.*\})\s*```", raw_text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    start_index = raw_text.find("{")
    end_index = raw_text.rfind("}")
    if start_index != -1 and end_index != -1 and end_index > start_index:
        return raw_text[start_index : end_index + 1].strip()
    return raw_text


def normalize_suggestions(value: Any) -> list[str]:
    """Normalize suggestions into a flat list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [line.strip(" -\t") for line in value.splitlines() if line.strip()]
    if isinstance(value, list):
        normalized: list[str] = []
        for item in value:
            if isinstance(item, str):
                cleaned = item.strip()
                if cleaned:
                    normalized.append(cleaned)
            elif isinstance(item, dict):
                text = str(item.get("text") or item.get("suggestion") or item.get("message") or "").strip()
                if text:
                    normalized.append(text)
            else:
                text = str(item).strip()
                if text:
                    normalized.append(text)
        return normalized
    text = str(value).strip()
    return [text] if text else []


def normalize_quality_score(value: Any) -> int:
    """Convert the model score into an integer percentage in the 0-100 range."""
    try:
        score = int(float(value))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))


def normalize_severity(value: Any) -> str:
    """Normalize a severity string to one of Low, Medium, High, or Critical."""
    if value is None:
        return "Low"
    text = str(value).strip().capitalize()
    if text in {"Low", "Medium", "High", "Critical"}:
        return text
    lower_text = str(value).strip().lower()
    if lower_text in {"info", "informational"}:
        return "Low"
    return "Low"


def derive_overall_severity(findings: list[SecurityFindingAnalysis], candidate: Any = None) -> str:
    """Choose the highest severity from the findings, falling back to the model label."""
    severity_order = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    highest = "Low"

    for finding in findings:
        if severity_order.get(finding.severity, 0) > severity_order.get(highest, 0):
            highest = finding.severity

    candidate_severity = normalize_severity(candidate)
    if severity_order.get(candidate_severity, 0) > severity_order.get(highest, 0):
        return candidate_severity
    return highest


def normalize_security_findings(value: Any) -> list[SecurityFindingAnalysis]:
    """Convert model findings into validated security finding objects."""
    if not isinstance(value, list):
        return []

    findings: list[SecurityFindingAnalysis] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        issue = str(item.get("issue") or item.get("vulnerability") or item.get("type") or "Security issue").strip()
        severity = normalize_severity(item.get("severity"))
        description = str(item.get("description") or item.get("summary") or "").strip()
        evidence = str(item.get("evidence") or item.get("location") or "").strip()
        recommendation = str(item.get("recommendation") or item.get("fix") or item.get("mitigation") or "").strip()
        if not description and not evidence and not recommendation:
            continue
        findings.append(
            SecurityFindingAnalysis(
                issue=issue,
                severity=severity,
                description=description,
                evidence=evidence,
                recommendation=recommendation,
            )
        )
    return findings


def normalize_improved_code(value: Any) -> str:
    """Normalize refactored code into a single readable string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            text = str(item).rstrip()
            if text:
                lines.append(text)
        return "\n".join(lines).strip()
    if isinstance(value, dict):
        preferred_keys = ("improved_code", "refactored_code", "code", "content", "text")
        for key in preferred_keys:
            candidate = value.get(key)
            if candidate:
                return normalize_improved_code(candidate)
        lines: list[str] = []
        for item in value.values():
            text = str(item).rstrip()
            if text:
                lines.append(text)
        return "\n".join(lines).strip()
    return str(value).strip()


def normalize_test_code(value: Any) -> str:
    """Normalize generated pytest code into a single executable string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return extract_code_text(value).strip()
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            text = str(item).rstrip()
            if text:
                lines.append(text)
        return "\n".join(lines).strip()
    if isinstance(value, dict):
        preferred_keys = ("test_code", "tests", "code", "content", "text")
        for key in preferred_keys:
            candidate = value.get(key)
            if candidate:
                return normalize_test_code(candidate)
        lines: list[str] = []
        for item in value.values():
            text = str(item).rstrip()
            if text:
                lines.append(text)
        return "\n".join(lines).strip()
    return str(value).strip()


def extract_code_text(raw_text: str) -> str:
    """Extract code from fenced markdown or plain model output."""
    fenced_match = re.search(r"```(?:python|pytest|text)?\s*(.*?)\s*```", raw_text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    return raw_text


def normalize_markdown_documentation(value: Any) -> str:
    """Normalize documentation output into a single markdown string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return extract_markdown_text(value).strip()
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            text = str(item).rstrip()
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
    if isinstance(value, dict):
        preferred_keys = ("markdown_documentation", "documentation", "markdown", "content", "text")
        for key in preferred_keys:
            candidate = value.get(key)
            if candidate:
                return normalize_markdown_documentation(candidate)
        parts: list[str] = []
        for item in value.values():
            text = str(item).rstrip()
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
    return str(value).strip()


def extract_markdown_text(raw_text: str) -> str:
    """Extract markdown text from fenced output when the model wraps the response."""
    fenced_match = re.search(r"```(?:markdown|md|text)?\s*(.*?)\s*```", raw_text, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()
    return raw_text


def build_fallback_unit_test_code(source_code: str, *, file_name: str) -> str:
    """Build a minimal executable pytest module when the model omits test code."""
    test_template = '''import pytest


def test_placeholder_happy_path():
    # Replace this placeholder with tests generated from {file_name}.
    assert True


def test_placeholder_edge_case():
    # Placeholder edge-case assertion for generated tests.
    assert True


def test_placeholder_invalid_input():
    # Placeholder invalid-input assertion for generated tests.
    assert True


def test_placeholder_exception_path():
    # Placeholder exception-path assertion for generated tests.
    assert True
'''
    return test_template.format(file_name=file_name).strip()


def build_fallback_documentation_markdown(
    source_code: str,
    *,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Build a minimal Markdown documentation skeleton when the model omits markdown."""
    code_fence_lang = language.lower() if language != "Unknown" else "text"
    return (
        f"# Overview\n\n"
        f"Documentation for `{file_name}` written in {language}. "
        f"(The AI model's response could not be validated, so this is a minimal fallback outline.)\n\n"
        f"# Language & Syntax Primer\n\n"
        f"- This file is written in {language}.\n\n"
        f"# Line-by-Line Walkthrough\n\n"
        f"- Re-run the documentation generator, or review the code below manually.\n\n"
        f"# Inputs\n\n"
        f"- List and explain the expected inputs.\n\n"
        f"# Outputs\n\n"
        f"- Describe the outputs and return values.\n\n"
        f"# Worked Example\n\n"
        f"- Trace through the code with a concrete sample input.\n\n"
        f"# Common Pitfalls\n\n"
        f"- Re-run generation for a full analysis.\n\n"
        f"# Usage Examples\n\n"
        f"```{code_fence_lang}\n"
        f"{source_code.strip()}\n"
        f"```\n\n"
        f"_Review context_: {review_context or 'No additional context provided.'}\n"
    ).strip()


def ensure_documentation_markdown(
    markdown: str,
    *,
    source_code: str,
    language: str,
    file_name: str,
    review_context: str,
) -> str:
    """Ensure the markdown response contains all required documentation sections."""
    if documentation_has_required_sections(markdown):
        return markdown.strip()
    return build_fallback_documentation_markdown(
        source_code,
        language=language,
        file_name=file_name,
        review_context=review_context,
    )


def documentation_has_required_sections(markdown: str) -> bool:
    """Check whether the markdown includes every required documentation heading."""
    if not markdown.strip():
        return False
    normalized = markdown.lower()
    return all(heading.lower() in normalized for heading in REQUIRED_DOCUMENTATION_HEADINGS)