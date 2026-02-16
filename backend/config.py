import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database (Lenovo Tiny) - read from POSTGRES_* env vars
    DB_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    DB_USER: str = os.getenv("POSTGRES_USER", "zoom_admin")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    DB_NAME: str = os.getenv("POSTGRES_DB", "zoom_dx_db")
    
    # Ollama (Docker service name)
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://ollama:11434")
    OLLAMA_MODEL: str = "llama3.2:3b"
    
    # e-Stat API
    ESTAT_APP_ID: str = os.getenv("ESTAT_APP_ID", "")
    
    # Paths
    DATA_DIR: str = os.getenv("DATA_DIR", "./data")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()
