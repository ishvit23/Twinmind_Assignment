import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.database.connection import get_db
from app.services.embedding_service import EmbeddingService
from app.services.faiss_service import FaissService
from app.services.llm.query_service import GeminiService
from app.models.chunk import Chunk   # FIXED IMPORT
from app.models.document import Document

logger = logging.getLogger(__name__)

# Use correct embedding size
faiss_service = FaissService(dim=1536)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    user_id: str = "default_user"
    top_k: int = 5
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# ----------------------------------------------------------------------
# SIMPLE KEYWORD SEARCH
# ----------------------------------------------------------------------
@router.post("/query")
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    try:
        logger.info(f"Query received: {request.query}")

        chunks = db.query(Chunk).all()
        if not chunks:
            return {
                "status": "success",
                "query": request.query,
                "results": [],
                "message": "No documents found"
            }

        q = request.query.lower()
        matched = [
            c for c in chunks
            if q in c.content.lower()
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
        logger.error("Keyword query failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------
# FULL RAG PIPELINE
# ----------------------------------------------------------------------
@router.post("/rag")
async def rag(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        # Filter chunks
        q = db.query(Chunk)

        # Filter by user_id
        if request.user_id:
            q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))

        # Date filter
        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        chunks = q.all()
        logger.info(f"Loaded {len(chunks)} chunks for RAG query")

        if not chunks:
            return {
                "status": "success",
                "answer": "No data found for this user.",
                "sources": []
            }

        # Build FAISS
        faiss_service.build_index(chunks)

        # Query embedding
        query_emb = EmbeddingService.get_embedding(request.query)

        results = faiss_service.search(query_emb, request.top_k)
        if not results:
            results = []

        context = "\n".join([c for c, _ in results])

        # Create LLM prompt
        prompt = f"""
Use ONLY the context below to answer.

Context:
{context}

Question:
{request.query}

Answer:
"""

        answer = GeminiService.generate_answer(prompt)

        return {
            "status": "success",
            "answer": answer,
            "sources": [c for c, _ in results]
        }

    except Exception as e:
        logger.error("RAG error", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------------------------------------
# PURE SEMANTIC SEARCH (no LLM)
# ----------------------------------------------------------------------
@router.post("/semantic-search")
async def semantic_search(request: QueryRequest, db: Session = Depends(get_db)):
    try:
        q = db.query(Chunk)

        # Date filters
        if request.start_date:
            q = q.filter(Chunk.created_at >= request.start_date)
        if request.end_date:
            q = q.filter(Chunk.created_at <= request.end_date)

        # User filter
        q = q.join(Document).filter(Document.doc_metadata.contains(f"uploaded_by:{request.user_id}"))

        chunks = q.all()

        faiss_service.build_index(chunks)
        query_emb = EmbeddingService.get_embedding(request.query)
        results = faiss_service.search(query_emb, request.top_k)

        return {
            "status": "success",
            "query": request.query,
            "results": [
                {
                    "content": c,
                    "distance": d
                }
                for c, d in results
            ]
        }

    except Exception as e:
        logger.error("Semantic search failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
