# app/services/embedding_service.py
import logging
from sentence_transformers import SentenceTransformer
import numpy as np
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class EmbeddingService:
    # Force MiniLM L6-v2 (384 dims)
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    dim = 384

    @staticmethod
    def get_dim():
        return EmbeddingService.dim

    @staticmethod
    def get_embedding(text: str):
        if not text:
            return None
        emb = EmbeddingService.model.encode(text)
        return np.array(emb, dtype="float32").tolist()
