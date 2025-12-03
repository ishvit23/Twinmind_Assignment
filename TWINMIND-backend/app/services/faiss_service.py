import numpy as np
import faiss
from app.services.embedding_service import EmbeddingService


class FaissService:

    def __init__(self):
        self.dimension = EmbeddingService.get_dim()  # expected embedding size
        self.index = None
        self.chunks = []

    def build_index(self, all_chunks):
        """
        Build FAISS index from valid chunks.
        A chunk is valid ONLY if:
        - embedding exists
        - embedding is a list
        - embedding length == dimension
        """

        valid_chunks = []
        valid_vectors = []

        for c in all_chunks:
            emb = c.embedding

            if emb is None:
                continue
            if not isinstance(emb, list):
                continue
            if len(emb) != self.dimension:
                continue

            # convert to float32 numpy
            vector = np.array(emb, dtype=np.float32)

            valid_chunks.append(c)
            valid_vectors.append(vector)

        # no valid embeddings — clear index
        if not valid_vectors:
            self.index = None
            self.chunks = []
            return

        # build FAISS index
        vectors_np = np.vstack(valid_vectors)

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors_np)

        self.chunks = valid_chunks

    def search(self, query_embedding, top_k=5):
        """
        Search similar chunks.
        """

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
