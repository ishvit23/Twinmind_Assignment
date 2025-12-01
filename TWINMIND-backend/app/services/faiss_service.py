import faiss
import numpy as np

class FaissService:
    def __init__(self, dim=1536):  # MUST MATCH embedding size
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.chunks = []   # store entire chunk object
        self.embeddings = []

    def build_index(self, all_chunks):
        """Rebuild the FAISS index from database chunk objects"""
        self.chunks = [c for c in all_chunks if c.embedding is not None]
        self.embeddings = [c.embedding for c in self.chunks]

        if not self.embeddings:
            # empty index
            self.index = faiss.IndexFlatL2(self.dim)
            return

        # recreate index with correct dimension
        self.index = faiss.IndexFlatL2(self.dim)
        embeddings_np = np.array(self.embeddings, dtype=np.float32)
        self.index.add(embeddings_np)

    def search(self, query_embedding, top_k=5):
        """Return list of (ChunkObject, distance)"""
        if not self.embeddings:
            return []

        if query_embedding is None:
            return []

        query_np = np.array([query_embedding], dtype=np.float32)

        distances, indices = self.index.search(query_np, top_k)
        results = []

        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue

            chunk_obj = self.chunks[idx]
            results.append((chunk_obj, dist))

        return results
