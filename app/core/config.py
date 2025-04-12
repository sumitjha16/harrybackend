import os
from pathlib import Path
from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings"""
    APP_NAME: str = "Storybook AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "TheBloke/Mistral-7B-Instruct-v0.1-GGUF")
    MODEL_FILENAME: str = os.getenv("MODEL_FILENAME", "mistral-7b-instruct-v0.1.Q4_K_M.gguf")
    MODEL_TYPE: str = "mistral"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # RAG settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 128
    RETRIEVAL_K: int = 5

    # LLM generation settings
    MAX_NEW_TOKENS: int = 512
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.95
    TOP_K: int = 50

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    CHROMA_DB_DIR: Path = DATA_DIR / "processed" / "chroma_db"
    MODEL_NAME: str = "mistral-small"

    # Model inference settings
    BATCH_SIZE: int = 1
    INFERENCE_THREADS: int = os.cpu_count() or 4

    # Performance optimizations
    RESPONSE_CACHE_SIZE: int = 100
    RESPONSE_CACHE_TTL: int = 3600  # seconds

    # Monitoring
    ENABLE_METRICS: bool = True
    PROMETHEUS_ENDPOINT: str = "/metrics"


@lru_cache()
def get_settings():
    """Get cached settings"""
    return Settings()