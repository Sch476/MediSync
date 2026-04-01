"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017/medisync"
    DB_NAME: str = "medisync"

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # LLM Provider: "huggingface" or "gemini"
    LLM_PROVIDER: str = "huggingface"

    # Hugging Face
    HF_API_TOKEN: Optional[str] = None
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Gemini
    GEMINI_API_KEY: Optional[str] = None

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_data"

    # App
    APP_NAME: str = "MediSync"
    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


settings = Settings()
