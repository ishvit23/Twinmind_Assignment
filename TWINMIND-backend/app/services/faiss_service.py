# app/services/faiss_service.py

import numpy as np
import faiss
from app.services.embedding_service import EmbeddingService


class FaissService:
    def __init__(self):
        self.dimension = EmbeddingService.get_dim()
        self.index = None
        self.chunks = []

    def build_index(self, all_chunks):
        # Filter only chunks that actually have embeddings
        self.chunks = [
            c for c in all_chunks
            if c.embedding is not None and len(c.embedding) > 0
        ]

        if not self.chunks:
            self.index = None
            return

        # Convert embeddings → float32 numpy array for FAISS
        embeddings = np.array(
            [np.array(c.embedding, dtype="float32") for c in self.chunks],
            dtype="float32"
        )

        # Create new FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)

    def search(self, query_embedding, top_k=5):
        if self.index is None:
            return []

        query_np = np.array(query_embedding, dtype="float32").reshape(1, -1)
        distances, indices = self.index.search(query_np, top_k)

        results = []
        for i, dist in zip(indices[0], distances[0]):
            if i == -1:
                continue
            chunk = self.chunks[i]
            results.append((chunk, float(dist)))

        return results
