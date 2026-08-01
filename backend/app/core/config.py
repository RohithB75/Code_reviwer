from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Code Reviewer API"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8501"])
    log_level: str = "INFO"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    ollama_timeout_seconds: float = 30.0
    openai_api_key: str = ""
    model_name: str = ""

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> list[str]:
        if value is None or value == "":
            return ["http://localhost:3000", "http://localhost:8501"]
        if isinstance(value, str):
            text = value.strip()
            # try JSON array first (e.g. ["http://...","http://..."])
            try:
                import json

                parsed = json.loads(text)
                if isinstance(parsed, list):
                    return [str(origin).strip() for origin in parsed if str(origin).strip()]
            except Exception:
                pass
            # fallback to comma-separated list
            return [origin.strip() for origin in text.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        text = str(value).strip()
        return [text] if text else []

    @field_validator("ollama_timeout_seconds", mode="before")
    @classmethod
    def parse_ollama_timeout_seconds(cls, value: object) -> float:
        if value is None or value == "":
            return 30.0
        return float(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
