# app/routes/query.py
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.database.connection import get_db
from app.models.chunk import Chunk
from app.models.document import Document

# Your actual file structure → embedding_service is NOT inside llm
from app.services.embedding_service import EmbeddingService
from app.services.llm.query_service import GeminiService, faiss_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    top_k: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ------------------------------------------------------------
# 🔎 SIMPLE KEYWORD SEARCH
# ------------------------------------------------------------
@router.post("/query")
async def keyword_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        if request.user_id:
            q = q.join(Document).filter(
                Document.doc_metadata.contains(f"uploaded_by:{request.user_id}")
            )

        chunks = q.all()

        if not chunks:
            return {
                "status": "success",
                "query": request.query,
                "results": [],
                "message": "No documents found"
            }

        query_lower = request.query.lower()

        matched = [
            c for c in chunks
            if query_lower in (c.content or "").lower()
        ][:request.top_k]

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
                }
                for c in matched
            ]
        }

    except Exception as e:
        logger.error("Keyword query error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# 🤖 FULL RAG PIPELINE
# ------------------------------------------------------------
@router.post("/rag")
async def rag(req: QueryRequest, db: Session = Depends(get_db)):
    try:
        chunks_query = (
            db.query(Chunk)
            .join(Document)
            .filter(Document.doc_metadata.contains(f"uploaded_by:{req.user_id}"))
        )

        if req.start_date:
            chunks_query = chunks_query.filter(Chunk.created_at >= req.start_date)
        if req.end_date:
            chunks_query = chunks_query.filter(Chunk.created_at <= req.end_date)

        chunks = chunks_query.all()

        if not chunks:
            return {"answer": "No relevant data found.", "sources": []}

        # Build FAISS index
        faiss_service.build_index(chunks)

        # Embed user query
        query_emb = EmbeddingService.get_embedding(req.query)
        results = faiss_service.search(query_emb, req.top_k)

        if not results:
            return {"answer": "No relevant information found.", "sources": []}

        context = "\n\n".join([c.content for c, _ in results])

        answer = GeminiService.answer(req.query, context)

        return {
            "answer": answer,
            "sources": [c.content[:200] for c, _ in results]
        }

    except Exception as e:
        logger.error("RAG error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# 🧠 SEMANTIC SEARCH
# ------------------------------------------------------------
@router.post("/semantic-search")
async def semantic_search_route(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        if request.user_id:
            q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))

        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)

        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        chunks = q.all()

        if not chunks:
            return {"status": "success", "results": []}

        faiss_service.build_index(chunks)

        query_emb = EmbeddingService.get_embedding(request.query)
        if query_emb is None:
            return {"status": "success", "results": []}

        results = faiss_service.search(query_emb, request.top_k)

        return {
            "status": "success",
            "query": request.query,
            "results": [
                {"content": c.content, "distance": d} for c, d in results
            ]
        }

    except Exception as e:
        logger.error("Semantic search error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
