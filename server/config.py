"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017/medisync"
    DB_NAME: str = "medisync"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    LLM_PROVIDER: str = "huggingface"

    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

    GEMINI_API_KEY: Optional[str] = None

    CHROMA_PERSIST_DIR: str = "./chroma_data"

    APP_NAME: str = "MediSync"
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()
