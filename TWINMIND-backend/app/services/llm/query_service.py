# app/services/llm/query_service.py

import logging
import os
from dotenv import load_dotenv
import google.generativeai as genai

from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService

load_dotenv()

# Gemini API key is automatically picked from environment
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

logger = logging.getLogger(__name__)

# Global FAISS instance (auto-uses correct dim)
faiss_service = FaissService()


class GeminiService:
    @staticmethod
    def answer(query: str, context: str) -> str:
        """
        Generate answer from Gemini using provided context.
        """
        prompt = (
            "You are a helpful AI assistant. Use ONLY the given context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n\n"
            "Provide a clear and concise answer."
        )
        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "LLM error: could not generate answer."


def semantic_search(query: str, top_k: int = 5):
    """
    Perform FAISS search.
    Returns: [(ChunkObject, distance),...]
    """
    query_embedding = EmbeddingService.get_embedding(query)
    if query_embedding is None:
        return []

    return faiss_service.search(query_embedding, top_k=top_k)


def generate_rag_answer(query: str, top_k: int = 5):
    """
    Full pipeline: semantic search → LLM answer
    """
    relevant = semantic_search(query, top_k=top_k)

    if not relevant:
        return "No relevant information found.", []

    # Join all chunk contents to form the context
    context = "\n\n---\n\n".join(
        [chunk_obj.content for chunk_obj, _ in relevant]
    )

    answer = GeminiService.answer(query, context)

    return answer, relevant
