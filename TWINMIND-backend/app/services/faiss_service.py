# app/services/faiss_service.py
import numpy as np
import faiss
import logging
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class FaissService:

    def __init__(self):
        self.dimension = EmbeddingService.get_dim()
        self.index = None
        self.chunks = []

    def build_index(self, all_chunks):
        logger.info(f"[FAISS] Building index — total chunks received: {len(all_chunks)}")

        valid_chunks = []
        valid_vectors = []

        for c in all_chunks:
            emb = c.embedding
            if emb is None:
                logger.warning(f"[FAISS] Chunk {c.id} has NO embedding")
                continue

            if not isinstance(emb, list):
                logger.error(f"[FAISS] Chunk {c.id} embedding is NOT a list")
                continue

            if len(emb) != self.dimension:
                logger.error(
                    f"[FAISS] Chunk {c.id} embedding wrong size: {len(emb)} != {self.dimension}"
                )
                continue

            valid_chunks.append(c)
            valid_vectors.append(np.array(emb, dtype=np.float32))

        logger.info(f"[FAISS] Valid embeddings: {len(valid_vectors)}")

        if not valid_vectors:
            logger.error("[FAISS] No valid embeddings — FAISS index will NOT be created")
            self.index = None
            self.chunks = []
            return

        vectors_np = np.vstack(valid_vectors)
        logger.info(f"[FAISS] FAISS array shape: {vectors_np.shape}")

        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(vectors_np)

        logger.info(f"[FAISS] Index built successfully with {len(valid_chunks)} vectors")

        self.chunks = valid_chunks

    def search(self, query_embedding, top_k=5):
        logger.info("[FAISS] Starting search")

        if self.index is None:
            logger.error("[FAISS] Search FAILED — index is None")
            return []

        query_np = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        logger.info(f"[FAISS] Query vector shape: {query_np.shape}")

        distances, indices = self.index.search(query_np, top_k)
        logger.info(f"[FAISS] Search results — distances: {distances}, indices: {indices}")

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                logger.warning("[FAISS] Returned index -1 — skipping")
                continue
            if idx >= len(self.chunks):
                logger.error(f"[FAISS] Index {idx} out of range")
                continue

            results.append((self.chunks[idx], float(dist)))

        logger.info(f"[FAISS] Final results count: {len(results)}")
        return results
