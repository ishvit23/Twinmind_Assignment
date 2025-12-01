import logging
from sentence_transformers import SentenceTransformer
from app.config import get_settings
import numpy as np

logger = logging.getLogger(__name__)
settings = get_settings()

class EmbeddingService:
    model = SentenceTransformer(settings.EMBEDDING_MODEL)

    @staticmethod
    def get_dim():
        return settings.EMBEDDING_DIMENSION

    @staticmethod
    def get_embedding(text: str):
        if not text:
            return None
        emb = EmbeddingService.model.encode(text)
        return np.array(emb, dtype="float32").tolist()
