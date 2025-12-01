import logging
import os
import google.generativeai as genai
from dotenv import load_dotenv

from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService

load_dotenv()
logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use your updated FAISS (NO arguments!)
faiss_service = FaissService()


# ---------------------------
#  GEMINI LLM SERVICE
# ---------------------------
class GeminiService:
    @staticmethod
    def generate_answer(query: str, context: str) -> str:
        """
        Generate an LLM answer using Gemini 2.5 Pro.
        Uses RAG context + user query.
        """

        prompt = (
            "You are a helpful, factual AI assistant.\n"
            "Answer ONLY using the provided context.\n\n"
            f"Context:\n{context}\n\n"
            f"User Question:\n{query}\n\n"
            "Give a clear, concise answer."
        )

        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return "LLM error: unable to generate response."


# ---------------------------
#  SEMANTIC SEARCH
# ---------------------------
def semantic_search(query: str, top_k: int = 5):
    """
    (1) Embed user query  
    (2) Search FAISS index  
    (3) Return top chunks  
    """

    try:
        query_embedding = EmbeddingService.get_embedding(query)

        if query_embedding is None:
            return []

        results = faiss_service.search(query_embedding, top_k)

        # results = [(ChunkObject, distance)]
        return results

    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return []


# ---------------------------
#  RAG PIPELINE
# ---------------------------
def generate_rag_answer(query: str, top_k: int = 5):
    """
    FULL PIPELINE:
    1) Semantic Search → retrieves relevant chunks  
    2) Build context from chunks  
    3) Ask Gemini to generate a factual answer  
    """

    retrieved = semantic_search(query, top_k)

    if not retrieved:
        return "No relevant information found.", []

    # Create RAG context from chunk content
    context = "\n".join([chunk.content for chunk, dist in retrieved])

    # Generate Gemini answer
    answer = GeminiService.generate_answer(query, context)

    return answer, retrieved
