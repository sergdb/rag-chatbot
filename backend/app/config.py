from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/docqa"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    chunk_size: int = 800
    chunk_overlap: int = 100
    rag_top_k: int = 6
    max_upload_mb: int = 20

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
