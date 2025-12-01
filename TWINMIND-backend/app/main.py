from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

load_dotenv()

from app.config import get_settings
from app.database.connection import init_db, engine
from app.database.base import Base

from app.routes.ingest import router as ingest_router
from app.routes.query import router as query_router
from app.routes.websocket import router as ws_router
from app.routes.auth import router as auth_router

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
settings = get_settings()


# -------------------------------------------------------
# LIFESPAN (startup + shutdown)
# -------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 TwinMind Backend Starting...")

    # Create tables on startup (important for Render)
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables ready")
    except Exception as e:
        logger.error(f"❌ Table creation failed: {e}")

    # Init DB connection
    try:
        init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")

    yield
    logger.info("🛑 TwinMind Backend Shutting down...")


# -------------------------------------------------------
# FASTAPI APP
# -------------------------------------------------------
app = FastAPI(
    title="TwinMind API",
    description="AI-powered knowledge management system",
    version="1.0.0",
    lifespan=lifespan
)


# -------------------------------------------------------
# CORS
# -------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------
# ROUTERS
# -------------------------------------------------------
app.include_router(auth_router, prefix="/api", tags=["Authentication"])
app.include_router(ingest_router, prefix="/api", tags=["Ingestion"])
app.include_router(query_router, prefix="/api", tags=["Query"])
app.include_router(ws_router, tags=["WebSocket"])


# -------------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TwinMind Backend"
    }


# -------------------------------------------------------
# ROOT ENDPOINT
# -------------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Welcome to TwinMind API",
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/auth/register, /api/auth/login",
            "ingest": "/api/ingest/upload",
            "query": "/api/query, /api/rag",
            "websocket": "/ws/query"
        }
    }


# -------------------------------------------------------
# REMOVE DUPLICATE RAG ENDPOINT
# (Query router already provides /api/rag)
# -------------------------------------------------------


# -------------------------------------------------------
# LOCAL DEVELOPMENT ENTRYPOINT
# -------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
