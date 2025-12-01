# app/models/chunk.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from app.models.base import Base
from app.config import get_settings

settings = get_settings()

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    tokens = Column(Integer)

    # Use configured vector dimension
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")

