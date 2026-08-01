from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.prompts.registry import PROMPT_REGISTRY


@dataclass(frozen=True)
class PromptDefinition:
    name: str
    description: str
    template_path: Path


class PromptManager:
    def __init__(self, prompts_root: Path | None = None) -> None:
        self.prompts_root = prompts_root or Path(__file__).resolve().parent / "templates"

    def list_prompts(self) -> list[PromptDefinition]:
        """Return all registered prompt definitions in a stable order."""
        return [self._build_definition(name, meta) for name, meta in PROMPT_REGISTRY.items()]

    def get_prompt(self, name: str, **placeholders: str) -> str:
        """Load a prompt template and render it with the provided placeholders."""
        definition = self._get_definition(name)
        template = definition.template_path.read_text(encoding="utf-8")
        return template.format(**placeholders)

    def get_template_path(self, name: str) -> Path:
        """Return the on-disk path for a registered prompt template."""
        return self._get_definition(name).template_path

    def _get_definition(self, name: str) -> PromptDefinition:
        if name not in PROMPT_REGISTRY:
            raise KeyError(f"Unknown prompt '{name}'.")
        return self._build_definition(name, PROMPT_REGISTRY[name])

    def _build_definition(self, name: str, metadata: dict[str, str]) -> PromptDefinition:
        return PromptDefinition(
            name=name,
            description=metadata["description"],
            template_path=self.prompts_root / metadata["file"],
        )
