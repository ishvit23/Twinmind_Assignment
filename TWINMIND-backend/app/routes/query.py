import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.connection import get_db
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pgvector.sqlalchemy import Vector
from app.models.document import Chunk
from app.services.faiss_service import FaissService
from app.services.llm.query_service import GeminiService

faiss_service = FaissService(dim=384)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    top_k: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@router.post("/query")
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Query: {request.query}")
        
        # Get all chunks (simple search for now)
        chunks = db.query(Chunk).all()
        
        if not chunks:
            return {
                "status": "success",
                "query": request.query,
                "results": [],
                "message": "No documents found"
            }
        
        # Simple keyword matching (replace with embeddings later)
        query_lower = request.query.lower()
        matched_chunks = [
            chunk for chunk in chunks 
            if query_lower in chunk.content.lower()
        ][:request.top_k]
        
        return {
            "status": "success",
            "query": request.query,
            "results_count": len(matched_chunks),
            "results": [
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.id,
                    "content": chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content,
                    "relevance_score": 0.95
                }
                for chunk in matched_chunks
            ]
        }
    except Exception as e:
        logger.error(f"Query failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag")
async def rag(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        query = db.query(Chunk)
        if request.user_id:
            query = query.filter(Chunk.document.has(doc_metadata=f"uploaded_by:{request.user_id}"))
        all_chunks = query.all() or []
        logging.info(f"Loaded {len(all_chunks)} chunks for user {request.user_id}")
        for chunk in all_chunks:
            logging.info(f"Chunk: {chunk.content[:100]}")  # Print first 100 chars

        faiss_service.build_index(all_chunks)
        query_embedding = EmbeddingService.get_embedding(request.query)
        results = faiss_service.search(query_embedding, top_k=request.top_k)
        if results is None or (hasattr(results, 'size') and results.size == 0):
            results = []
        logging.info(f"FAISS returned {len(results)} results for query '{request.query}'")
        for content, distance in results:
            logging.info(f"Selected chunk: {content[:100]} (distance: {distance})")

        context = "\n".join([content for content, _ in results])
        logging.info(f"Context sent to LLM: {context[:500]}")  # Print first 500 chars

        prompt = f"Answer the following question using the provided context.\n\nContext:\n{context}\n\nQuestion: {request.query}"
        logging.info(f"Prompt sent to LLM: {prompt[:500]}")  # Print first 500 chars

        answer = GeminiService.generate_answer(prompt, context)
        return {
            "status": "success",
            "answer": answer,
            "sources": [content for content, _ in results]
        }
    except Exception as e:
        logging.error(f"RAG error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/semantic-search")
async def semantic_search(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Get all chunks for the user and date filters
        query = db.query(Chunk)
        if request.start_date:
            query = query.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            query = query.filter(Chunk.created_at <= request.end_date)
        if request.user_id:
            query = query.filter(Chunk.document.has(doc_metadata=f"uploaded_by:{request.user_id}"))
        all_chunks = query.all()

        # Build FAISS index
        faiss_service.build_index(all_chunks)

        # Get query embedding
        query_embedding = EmbeddingService.get_embedding(request.query)

        # Search
        results = faiss_service.search(query_embedding, top_k=request.top_k)
        if results is None or (hasattr(results, 'size') and results.size == 0):
            results = []

        return {
            "status": "success",
            "query": request.query,
            "results": [
                {
                    "content": content,
                    "distance": distance
                } for content, distance in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))