from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

from app.models.base import Base


class ModalityType(enum.Enum):
    PDF = "pdf"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    WEB = "web"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    modality = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    doc_metadata = Column(String)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete")
