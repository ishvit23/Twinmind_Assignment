# app/services/faiss_service.py
import faiss
import numpy as np
from app.services.embedding_service import EmbeddingService

class FaissService:
    def __init__(self):
        # auto-detect correct dimension from embedding service
        self.dim = EmbeddingService.get_dim()
        self.index = faiss.IndexFlatL2(self.dim)
        self.chunks = []       # store chunk objects
        self.embeddings = []   # store embeddings

    def build_index(self, all_chunks):
        """
        Build FAISS index from Chunk SQLAlchemy objects
        """
        # keep only chunks with embeddings
        self.chunks = [c for c in all_chunks if c.embedding is not None]
        self.embeddings = [c.embedding for c in self.chunks]

        # (re)create index
        self.index = faiss.IndexFlatL2(self.dim)
        if not self.embeddings:
            return

        embeddings_np = np.array(self.embeddings, dtype=np.float32)
        self.index.add(embeddings_np)

    def search(self, query_embedding, top_k=5):
        """
        Returns list of (ChunkObject, distance)
        """
        if not self.embeddings or query_embedding is None:
            return []

        query_np = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_np, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            results.append((self.chunks[idx], float(dist)))
        return results
