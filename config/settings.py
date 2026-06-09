"""Centralized configuration. No env var is read anywhere outside this module."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", populate_by_name=True)

    # --- LangSmith (optional) ---
    langsmith_tracing: bool = Field(default=False, validation_alias="LANGSMITH_TRACING")
    langsmith_api_key: str = Field(default="", validation_alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="marquee", validation_alias="LANGSMITH_PROJECT")

    # --- Local stores ---
    db_path: str = Field(default="marquee.db", validation_alias="MARQUEE_DB_PATH")
    chroma_dir: str = Field(default=".chroma", validation_alias="MARQUEE_CHROMA_DIR")

    # --- Outbound safety ---
    gmail_dry_run: bool = Field(default=True, validation_alias="MARQUEE_GMAIL_DRY_RUN")

    # --- Model-per-task table (LiteLLM ids; swap provider by changing these, not code) ---
    model_triage: str = "anthropic/claude-haiku-4-5-20251001"
    model_qualify: str = "anthropic/claude-haiku-4-5-20251001"
    model_select: str = "anthropic/claude-haiku-4-5-20251001"
    model_draft: str = "anthropic/claude-sonnet-4-6"
    model_critique: str = "anthropic/claude-sonnet-4-6"
    # Eval judge: deliberately distinct (stronger tier) from the task models. See PROJECT_SPEC.
    judge_model: str = "anthropic/claude-opus-4-8"

    temperature_draft: float = 0.7
    temperature_deterministic: float = 0.0

    # --- Graph thresholds ---
    fit_threshold: float = 0.6
    max_revisions: int = 2

    # --- Embeddings (local, no API key) ---
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    @property
    def async_db_url(self) -> str:
        return f"sqlite+aiosqlite:///{self.db_path}"

    def apply_provider_env(self) -> None:
        """Make credentials available to LiteLLM / LangSmith. The only place env is written.

        Provider-neutral: loads the whole .env, so whichever provider key is present
        (ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, ...) is picked up by LiteLLM for the
        model ids configured below. No provider is named in code.
        """
        import os

        from dotenv import load_dotenv

        load_dotenv(override=False)
        if self.langsmith_tracing:
            os.environ.setdefault("LANGSMITH_TRACING", "true")
            os.environ.setdefault("LANGSMITH_API_KEY", self.langsmith_api_key)
            os.environ.setdefault("LANGSMITH_PROJECT", self.langsmith_project)


@lru_cache
def get_settings() -> Settings:
    return Settings()
