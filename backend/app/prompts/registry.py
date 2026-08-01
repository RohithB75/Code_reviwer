from __future__ import annotations

PROMPT_REGISTRY: dict[str, dict[str, str]] = {
    "code_review": {
        "file": "code_review.md",
        "description": "General purpose code review prompt.",
    },
    "security_review": {
        "file": "security_review.md",
        "description": "Prompt focused on security and vulnerability analysis.",
    },
    "performance_review": {
        "file": "performance_review.md",
        "description": "Prompt focused on runtime and resource efficiency.",
    },
    "complexity": {
        "file": "complexity.md",
        "description": "Prompt for evaluating complexity and maintainability.",
    },
    "unit_tests": {
        "file": "unit_tests.md",
        "description": "Prompt for identifying and proposing unit tests.",
    },
    "refactoring": {
        "file": "refactoring.md",
        "description": "Prompt for suggesting safe refactoring opportunities.",
    },
    "documentation": {
        "file": "documentation.md",
        "description": "Prompt for improving inline and external documentation.",
    },
}
