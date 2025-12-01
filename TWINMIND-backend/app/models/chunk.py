from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from app.models.base import Base
from app.services.embedding_service import EmbeddingService  # NEW IMPORT


# Auto-detect embedding dimension from SentenceTransformer model
EMBEDDING_DIM = EmbeddingService.model.get_sentence_embedding_dimension()


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    tokens = Column(Integer)

    # FIXED: use correct dimension instead of 1536
    embedding = Column(Vector(EMBEDDING_DIM))  

    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
