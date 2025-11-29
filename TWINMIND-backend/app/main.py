from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()

from app.config import get_settings
from app.database.connection import init_db
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.websocket import router as ws_router
from app.routes.auth import router as auth_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TwinMind Backend Starting...")
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
    yield
    logger.info("🛑 TwinMind Backend Shutting down...")

app = FastAPI(
    title="TwinMind API",
    description="AI-powered knowledge management system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api", tags=["Ingestion"])
app.include_router(query_router, prefix="/api", tags=["Query"])
app.include_router(ws_router, tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TwinMind Backend"
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to TwinMind API",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "auth": "/api/auth/register, /api/auth/login",
            "ingest": "/api/ingest/upload",
            "query": "/api/query, /api/rag",
            "websocket": "ws://localhost:8000/ws/query"
        }
    }

@app.post("/api/rag")
def rag_query(query: str):
    answer = query_service.generate_answer(query)
    return {"answer": answer}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )