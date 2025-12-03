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

from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService
from app.services.llm.query_service import GeminiService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Query"])

faiss_service = FaissService()


class QueryRequest(BaseModel):
    query: str
    user_id: str = "demo_user"
    top_k: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# -----------------------------------------------------
# 🔍 SIMPLE KEYWORD SEARCH
# -----------------------------------------------------
@router.post("/query")
async def keyword_query(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        # ❌ USER FILTER REMOVED (this was blocking all results)
        # If you need user filtering later, we will add a robust version

        chunks = q.all()

        if not chunks:
            return {"status": "success", "results": [], "message": "No documents found"}

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
                    "document_id": str(c.document_id),
                    "chunk_id": str(c.id),
                    "content": c.content[:300] + ("..." if len(c.content) > 300 else ""),
                    "relevance_score": 1.0,
                }
                for c in matched
            ],
        }

    except Exception as e:
        logger.error("Keyword query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------
# 🤖 FULL RAG PIPELINE
# -----------------------------------------------------
@router.post("/rag")
async def rag(req: QueryRequest, db: Session = Depends(get_db)):
    try:
        chunks_q = db.query(Chunk)

        # ❌ REMOVE METADATA FILTER — THIS BROKE EVERYTHING
        # If needed later we will re-add with regex support

        if req.start_date:
            chunks_q = chunks_q.filter(Chunk.created_at >= req.start_date)
        if req.end_date:
            chunks_q = chunks_q.filter(Chunk.created_at <= req.end_date)

        chunks = chunks_q.all()

        if not chunks:
            return {"answer": "No relevant data found.", "sources": []}

        faiss_service.build_index(chunks)

        query_emb = EmbeddingService.get_embedding(req.query)
        results = faiss_service.search(query_emb, req.top_k)

        if not results:
            return {"answer": "No relevant information found.", "sources": []}

        context = "\n\n".join([c.content for c, _ in results])
        answer = GeminiService.answer(req.query, context)

        return {
            "answer": answer,
            "sources": [
                {
                    "content": c.content[:500],
                    "distance": float(d),
                    "chunk_id": str(c.id),
                    "document_id": str(c.document_id)
                }
                for c, d in results
            ]
        }

    except Exception as e:
        logger.error("RAG error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------------------------
# 🧠 SEMANTIC SEARCH
# -----------------------------------------------------
@router.post("/semantic-search")
async def semantic_search_route(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        # ❌ FILTER REMOVED (same issue as RAG)

        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        chunks = q.all()

        if not chunks:
            return {"status": "success", "results": []}

        faiss_service.build_index(chunks)
        query_emb = EmbeddingService.get_embedding(request.query)

        if not query_emb:
            return {"status": "success", "results": []}

        results = faiss_service.search(query_emb, request.top_k)

        return {
            "status": "success",
            "query": request.query,
            "results": [
                {
                    "content": c.content,
                    "distance": float(d),
                    "chunk_id": str(c.id),
                    "document_id": str(c.document_id)
                }
                for c, d in results
            ]
        }

    except Exception as e:
        logger.error("Semantic search failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
