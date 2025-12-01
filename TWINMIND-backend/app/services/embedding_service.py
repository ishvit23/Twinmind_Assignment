import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)
load_dotenv()

class EmbeddingService:
    # MiniLM-L6-v2 → embeddings are 384-dimensional
    model = SentenceTransformer("all-MiniLM-L6-v2")

    @staticmethod
    def get_embedding(text: str) -> list[float]:
        """Generate embedding from text."""
        if not text or not isinstance(text, str):
            return None
        embedding = EmbeddingService.model.encode(text)
        return embedding.tolist()

    @staticmethod
    def get_dim() -> int:
        """Return embedding vector dimension."""
        return EmbeddingService.model.get_sentence_embedding_dimension()
