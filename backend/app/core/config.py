from functools import lru_cache
from pydantic import Field
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

    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    rate_limit_per_minute: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
