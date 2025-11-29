import logging
logger = logging.getLogger(__name__)

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class GeminiService:
    @staticmethod
    def generate_answer(prompt: str, context: str) -> str:
        full_prompt = f"{context}\n\nQuestion: {prompt}"
        model = genai.GenerativeModel("models/gemini-2.5-pro")
        response = model.generate_content(full_prompt)
        return response.text

class QueryService:
    def __init__(self):
        pass
    
    def search(self, query: str, chunks: list, top_k: int = 5):
        # Placeholder for semantic search
        return chunks[:top_k]
    
    def generate_answer(self, query: str, context: str):
        # Placeholder for LLM call
        return f"Answer based on: {context[:100]}..."

def semantic_search(query: str):
    query_embedding = EmbeddingService.get_embedding(query)
    results = faiss_service.search(query_embedding)
    return results

def generate_answer(query: str):
    context_chunks = semantic_search(query)
    context = "\n".join([chunk.content for chunk in context_chunks])
    answer = GeminiService.generate_answer(query, context)
    return answer