import faiss
import numpy as np
from app.config import get_settings

settings = get_settings()

class FaissService:
    def __init__(self, dim=None):
        self.dim = dim or settings.EMBEDDING_DIMENSION
        self.index = faiss.IndexFlatL2(self.dim)
        self.chunks = []
        self.embeddings = []

    def build_index(self, all_chunks):
    # Filter only chunks that actually have embeddings
    self.chunks = [
        c for c in all_chunks
        if c.embedding is not None and len(c.embedding) > 0
    ]

    if not self.chunks:
        self.index = None
        return

    embeddings = np.array([c.embedding for c in self.chunks], dtype="float32")

    self.index = faiss.IndexFlatL2(self.dimension)
    self.index.add(embeddings)


    def search(self, query_emb, top_k=5):
        if not query_emb or not self.embeddings:
            return []
        q = np.array([query_emb], dtype=np.float32)
        D, I = self.index.search(q, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(dist)))
        return results
