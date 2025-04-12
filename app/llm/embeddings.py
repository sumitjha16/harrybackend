import os
import logging
from pathlib import Path
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
# Updated import for Chroma
from langchain_chroma import Chroma
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

@lru_cache()
def get_embeddings_model():
    logger.info(f"Loading embeddings model: {settings.EMBEDDING_MODEL}")
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

def get_vector_store():
    embeddings = get_embeddings_model()
    if os.path.exists(settings.CHROMA_DB_DIR):
        logger.info(f"Loading existing vector store from {settings.CHROMA_DB_DIR}")
        return Chroma(
            persist_directory=str(settings.CHROMA_DB_DIR),
            embedding_function=embeddings
        )
    else:
        logger.error(f"Vector store not found at {settings.CHROMA_DB_DIR}")
        raise FileNotFoundError(
            f"Vector store not found at {settings.CHROMA_DB_DIR}. "
            f"Please ensure ChromaDB directory exists."
        )