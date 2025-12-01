# app/services/llm/query_service.py
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService

load_dotenv()
genai.configure(api_key=None)  # let environment var GEMINI_API_KEY be set

logger = logging.getLogger(__name__)

# global faiss service (uses embedding service dim)
faiss_service = FaissService()

class GeminiService:
    @staticmethod
    def generate_answer(prompt: str) -> str:
        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "LLM error: Could not generate answer."

def semantic_search(query: str, top_k: int = 5):
    query_embedding = EmbeddingService.get_embedding(query)
    if query_embedding is None:
        return []
    results = faiss_service.search(query_embedding, top_k=top_k)
    return results  # list of (ChunkObject, distance)

def generate_rag_answer(query: str, top_k: int = 5):
    relevant = semantic_search(query, top_k=top_k)
    if not relevant:
        return "No relevant information found.", []

    # Build context with chunk contents (keep in order returned)
    context = "\n\n---\n\n".join([chunk_obj.content for chunk_obj, _ in relevant])

    prompt = (
        "You are a helpful assistant. Answer using ONLY the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer concisely:"
    )

    answer = GeminiService.generate_answer(prompt)
    return answer, relevant  # return answer and list of (ChunkObject, distance)
