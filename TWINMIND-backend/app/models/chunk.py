from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid

from app.models.base import Base   # FIXED IMPORT


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    tokens = Column(Integer)

    embedding = Column(Vector(1536))  # or your EMBEDDING_DIMENSION
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="chunks")
