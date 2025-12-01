from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.base import Base  # correct import


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

    # Correct relationship (Chunk defined in chunk.py)
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
