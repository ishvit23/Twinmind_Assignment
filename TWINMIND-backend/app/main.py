from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()

from app.config import get_settings
from app.database.connection import init_db, engine
from app.models.base import Base

# IMPORTANT — import ALL models BEFORE create_all() to avoid missing-table issues
import app.models.document
import app.models.chunk
import app.models.user

# Routers
from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.websocket import router as ws_router
from app.routes.auth import router as auth_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

settings = get_settings()


# -------------------------------------------------------------------
# 👇 Lifespan — initializes DB cleanly (no circular imports)
# -------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TwinMind Backend Starting...")

    # Create DB tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")

    # Initialize DB connection
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")

    yield

    logger.info("🛑 TwinMind Backend Shutdown")


# -------------------------------------------------------------------
# 🌐 FastAPI App Initialization
# -------------------------------------------------------------------
app = FastAPI(
    title="TwinMind API",
    description="AI-powered knowledge management and RAG system",
    version="1.0.0",
    lifespan=lifespan
)

# -------------------------------------------------------------------
# 🔓 CORS (allow everything for Streamlit / local dev)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 📌 Routers
# -------------------------------------------------------------------
app.include_router(auth_router, prefix="/api", tags=["Auth"])
app.include_router(ingest_router, prefix="/api", tags=["Ingestion"])
app.include_router(query_router, prefix="/api", tags=["Query"])
app.include_router(ws_router, tags=["WebSocket"])


# -------------------------------------------------------------------
# 🏥 Health Check
# -------------------------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


# -------------------------------------------------------------------
# 🏠 Root Endpoint
# -------------------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Welcome to TwinMind API 🎉",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth",
            "ingest": "/api/ingest/upload",
            "rag": "/api/rag",
            "semantic_search": "/api/semantic-search",
            "query": "/api/query",
            "websocket": "/ws/query",
        }
    }


# -------------------------------------------------------------------
# 🖥 Local Dev Runner
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
