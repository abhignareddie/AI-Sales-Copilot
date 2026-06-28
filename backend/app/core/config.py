from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Sales Copilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v1"

    # Auth
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/ai_sales_copilot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "sales_knowledge"

    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: list[str] = [".pdf", ".docx", ".txt", ".csv"]

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI - OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # AI - Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-pro"
    LLM_PROVIDER: str = "gemini"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MOCK_EMBEDDINGS: bool = True

    # RAG
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5

    # Agent
    AGENT_MAX_RETRIES: int = 2
    AGENT_TIMEOUT: int = 120

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
