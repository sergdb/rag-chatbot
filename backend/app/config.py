from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# config.py -> app/ -> backend/
_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _env_file_paths() -> tuple[str, ...]:
    """Prefer repo-root .env, then backend/.env; cwd `.env` last."""
    candidates = (
        _REPO_ROOT / ".env",
        _BACKEND_ROOT / ".env",
        Path(".env"),
    )
    found = tuple(str(p.resolve()) for p in candidates if p.is_file())
    return found if found else (".env",)


class Settings(BaseSettings):
    """OpenAI model names and embedding size must be set via environment (see repo `.env.example`)."""

    model_config = SettingsConfigDict(
        env_file=_env_file_paths(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str = ""

    openai_chat_model: str
    openai_embedding_model: str
    openai_embedding_dimensions: int

    chunk_size: int = 800
    chunk_overlap: int = 100
    rag_top_k: int = 6
    max_upload_mb: int = 20


settings = Settings()
