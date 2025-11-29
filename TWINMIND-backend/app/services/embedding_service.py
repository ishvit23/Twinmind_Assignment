import logging
logger = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

from sentence_transformers import SentenceTransformer

class EmbeddingService:
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast, small, widely used

    @staticmethod
    def get_embedding(text: str) -> list[float]:
        if not text or not isinstance(text, str):
            return None
        embedding = EmbeddingService.model.encode(text)
        return embedding.tolist() if embedding is not None else None