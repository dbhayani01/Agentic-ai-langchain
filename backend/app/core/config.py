from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "AI Customer Support Assistant"
    environment: str = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"

    database_url: str = Field(default="postgresql+asyncpg://postgres:postgres@db:5432/support_ai")
    redis_url: str = Field(default="redis://redis:6379/0")

    cors_origins: list[str] = ["http://localhost:5173"]

    # OpenAI-compatible provider configuration (defaults tuned for Groq free/dev tier).
    llm_api_key: str = Field(default="", validation_alias=AliasChoices("LLM_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY"))
    llm_base_url: str = Field(
        default="https://api.groq.com/openai/v1",
        validation_alias=AliasChoices("LLM_BASE_URL", "OPENAI_BASE_URL", "GROQ_BASE_URL"),
    )
    llm_model: str = Field(
        default="llama-3.1-8b-instant",
        validation_alias=AliasChoices("LLM_MODEL", "OPENAI_MODEL", "GROQ_MODEL"),
    )

    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
