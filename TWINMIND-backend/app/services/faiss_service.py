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
        """
        Build a FAISS index from chunks that have valid embeddings.
        """

        # Filter only chunks that have a valid embedding list
        self.chunks = [
            c for c in all_chunks
            if c.embedding is not None and isinstance(c.embedding, list) and len(c.embedding) > 0
        ]

        if not self.chunks:
            self.index = None
            return

        # Convert embeddings to float32 numpy array
        embeddings = np.array(
            [np.array(c.embedding, dtype="float32") for c in self.chunks],
            dtype="float32"
        )

        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings)

    def search(self, query_embedding, top_k=5):
        """
        Search using FAISS and return matched chunks.
        """

        if self.index is None:
            return []

        # Convert query embedding to numpy array
        query_np = np.array(query_embedding, dtype="float32").reshape(1, -1)

        distances, indices = self.index.search(query_np, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue

            chunk = self.chunks[idx]
            results.append((chunk, float(dist)))

        return results
