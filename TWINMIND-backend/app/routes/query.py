# app/routes/query.py
import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database.connection import get_db
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService
from app.services.llm.query_service import GeminiService, faiss_service
from app.models.chunk import Chunk
from app.models.document import Document

logger = logging.getLogger(__name__)
router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    top_k: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

@router.post("/query")
async def keyword_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)
        if request.user_id:
            # join document and filter by metadata string
            q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))
        chunks = q.all()
        if not chunks:
            return {"status": "success", "query": request.query, "results": [], "message": "No documents found"}

        query_lower = request.query.lower()
        matched = [c for c in chunks if query_lower in (c.content or "").lower()][:request.top_k]

        return {
            "status": "success",
            "query": request.query,
            "results_count": len(matched),
            "results": [
                {
                    "document_id": c.document_id,
                    "chunk_id": str(c.id),
                    "content": c.content[:300] + ("..." if len(c.content) > 300 else ""),
                    "relevance_score": 1.0
                } for c in matched
            ]
        }
    except Exception as e:
        logger.error("Keyword query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rag")
async def rag(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        if request.user_id:
            q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))

        # date filters
        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        chunks = q.all()
        logger.info(f"Loaded {len(chunks)} chunks for user {request.user_id}")

        if not chunks:
            return {"status": "success", "answer": "No data found for this user.", "sources": []}

        # Build FAISS index from DB chunks
        faiss_service.build_index(chunks)

        # Get query embedding
        query_emb = EmbeddingService.get_embedding(request.query)
        if query_emb is None:
            return {"status": "success", "answer": "Could not create embedding for query.", "sources": []}

        results = faiss_service.search(query_emb, request.top_k)
        if not results:
            return {"status": "success", "answer": "No relevant results.", "sources": []}

        # Build context string from chunk contents
        context = "\n\n".join([getattr(chunk_obj, "content", "") for chunk_obj, _ in results])

        # Generate answer using Gemini
        answer = GeminiService.generate_answer(request.query, context)

        sources = [chunk_obj.content for chunk_obj, _ in results]

        return {"status": "success", "answer": answer, "sources": sources}
    except Exception as e:
        logger.error("RAG error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/semantic-search")
async def semantic_search(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)
        if request.user_id:
            q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))
        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        chunks = q.all()
        faiss_service.build_index(chunks)

        query_emb = EmbeddingService.get_embedding(request.query)
        if query_emb is None:
            return {"status":"success","results":[]}

        results = faiss_service.search(query_emb, request.top_k)

        return {
            "status": "success",
            "query": request.query,
            "results": [
                {"content": getattr(c, "content", ""), "distance": d} for c, d in results
            ]
        }
    except Exception as e:
        logger.error("Semantic search failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
