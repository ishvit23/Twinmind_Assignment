import numpy as np
import faiss
from app.services.embedding_service import EmbeddingService

class FaissService:

    def __init__(self):
        self.dimension = EmbeddingService.get_dim()
        self.index = None
        self.chunks = []

    def _to_list(self, emb):
        """
        Convert pgvector Vector -> python list
        """
        if emb is None:
            return None

        # pgvector returns something like Vector([....])
        # convert to Python list
        try:
            return list(emb)
        except Exception:
            return None

    def build_index(self, all_chunks):
        valid_chunks = []
        valid_vectors = []

        for c in all_chunks:
            raw_emb = c.embedding
            emb = self._to_list(raw_emb)

            if emb is None:
                print(f"[FAISS] Chunk {c.id} embedding invalid")
                continue

            if len(emb) != self.dimension:
                print(f"[FAISS] Chunk {c.id} dim mismatch {len(emb)} != {self.dimension}")
                continue

            vector = np.array(emb, dtype=np.float32)
            valid_chunks.append(c)
            valid_vectors.append(vector)

        if not valid_vectors:
            print("[FAISS] No valid embeddings — FAISS index cleared")
            self.index = None
            self.chunks = []
            return

        vectors_np = np.vstack(valid_vectors)

        print("[FAISS] Building index with shape:", vectors_np.shape)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors_np)

        self.chunks = valid_chunks
        print(f"[FAISS] Index built ({len(valid_chunks)} vectors)")

    def search(self, query_embedding, top_k=5):

        if self.index is None:
            print("[FAISS] Search failed — index is None")
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
