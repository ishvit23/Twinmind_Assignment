import faiss
import numpy as np

class FaissService:
    def __init__(self, dim=384):
        self.index = faiss.IndexFlatL2(dim)
        self.embeddings = []
        self.chunks = []

    def add_chunk(self, chunk_content, embedding):
        self.embeddings.append(embedding)
        self.chunks.append(chunk_content)
        self.index.add(np.array([embedding], dtype=np.float32))

    def build_index(self, all_chunks):
        if not all_chunks:
            self.embeddings = []
            self.chunks = []
            self.index = None
            return
        self.embeddings = [chunk.embedding for chunk in all_chunks if chunk.embedding is not None]
        self.chunks = [chunk.content for chunk in all_chunks if chunk.embedding is not None]
        if self.embeddings:
            import faiss
            self.index = faiss.IndexFlatL2(len(self.embeddings[0]))
            self.index.add(np.array(self.embeddings, dtype=np.float32))
        else:
            self.index = None

    def search(self, query_embedding, top_k=5):
        # query_embedding should be a list/array of floats
        if not self.embeddings or self.index is None or query_embedding is None:
            return []
        import numpy as np
        D, I = self.index.search(np.array([query_embedding], dtype=np.float32), top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            if idx == -1:
                continue
            chunk = self.chunks[idx]
            # If chunk is a string, use it directly
            if isinstance(chunk, str):
                results.append((chunk, dist))
            else:
                results.append((chunk.content, dist))
        return results