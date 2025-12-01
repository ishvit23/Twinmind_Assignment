from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Float
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum
from pgvector.sqlalchemy import Vector
from app.models.base import Base  # <-- Correct import

class ModalityType(enum.Enum):
    PDF = "pdf"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    WEB = "web"

class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String)
    modality = Column(Enum(ModalityType))
    file_path = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    doc_metadata = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chunks = relationship("Chunk", back_populates="document")

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_index = Column(Integer)
    content = Column(Text)
    tokens = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    embedding = Column(Vector(384))  # Use your embedding dimension

    document = relationship("Document", back_populates="chunks")
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")

