import logging
logger = logging.getLogger(__name__)

import google.generativeai as genai
import os
from dotenv import load_dotenv

from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Global FAISS service (same used in RAG)
faiss_service = FaissService(dim=384)


# ---------------------------
#  GEMINI LLM
# ---------------------------
class GeminiService:
    @staticmethod
    def generate_answer(query: str, context: str) -> str:
        """
        Creates an LLM answer based on user query + recalled context.
        """

        prompt = (
            "You are a helpful AI assistant. Use ONLY the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"User Question: {query}\n\n"
            "Answer clearly and concisely."
        )

        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "LLM error: Could not generate answer."


# ---------------------------
#  SEMANTIC SEARCH FUNCTIONS
# ---------------------------
def semantic_search(query: str, top_k: int = 5):
    """
    Uses FAISS + SentenceTransformer embeddings
    to retrieve the most relevant chunks.
    """
    try:
        query_embedding = EmbeddingService.get_embedding(query)

        if query_embedding is None:
            return []

        results = faiss_service.search(query_embedding, top_k=top_k)

        # results = [(chunk_text, distance), ...]
        return results

    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        return []


# ---------------------------
#  FULL PIPELINE (SEARCH + LLM)
# ---------------------------
def generate_rag_answer(query: str, top_k: int = 5):
    """
    (1) Get relevant chunks  
    (2) Build context  
    (3) Ask Gemini for an answer  
    """
    relevant = semantic_search(query, top_k=top_k)

    if not relevant:
        return "No relevant information found.", []

    # Build context string
    context = "\n".join([chunk_text for chunk_text, distance in relevant])

    answer = GeminiService.generate_answer(query, context)

    return answer, relevant
