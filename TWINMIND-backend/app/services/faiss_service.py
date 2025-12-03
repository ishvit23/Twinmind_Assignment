import numpy as np
import faiss
import ast  # NEW
from app.services.embedding_service import EmbeddingService


class FaissService:

    def __init__(self):
        self.dimension = EmbeddingService.get_dim()
        self.index = None
        self.chunks = []

    def _normalize_embedding(self, emb):
        """Normalize DB embedding into a proper Python list."""
        if emb is None:
            return None

        # Already good
        if isinstance(emb, list):
            return emb

        # pgvector sometimes returns string: "{0.1,0.2,0.3}"
        if isinstance(emb, str):
            try:
                emb = emb.replace("{", "[").replace("}", "]")
                return ast.literal_eval(emb)
            except:
                return None

        return None

    def build_index(self, all_chunks):

        valid_chunks = []
        valid_vectors = []

        for c in all_chunks:
            emb = self._normalize_embedding(c.embedding)   # 🔥 FIXED

            if emb is None:
                continue
            if len(emb) != self.dimension:
                continue

            vector = np.array(emb, dtype=np.float32)

            valid_chunks.append(c)
            valid_vectors.append(vector)

        if not valid_vectors:
            self.index = None
            self.chunks = []
            return

        vectors_np = np.vstack(valid_vectors)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors_np)

        self.chunks = valid_chunks

    def search(self, query_embedding, top_k=5):
        if self.index is None:
            return []

        query_np = np.array(query_embedding, dtype=np.float32).reshape(1, -1)

        distances, indices = self.index.search(query_np, top_k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            if idx >= len(self.chunks):
                continue

            results.append((self.chunks[idx], float(dist)))

        return results
