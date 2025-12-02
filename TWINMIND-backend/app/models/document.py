import uuid
from datetime import datetime
import enum

from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# IMPORTANT: Base must come ONLY from models.base
from app.models.base import Base


# -------------------------
# ENUM TYPE
# -------------------------
class ModalityType(enum.Enum):
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    WEB = "web"          # used for URL ingestion
    MARKDOWN = "markdown"
    OTHER = "other"


# -------------------------
# DOCUMENT MODEL
# -------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)

    modality = Column(Enum(ModalityType), nullable=False)

    # file_path is optional (web/text do not use it)
    file_path = Column(String, nullable=True)

    # uploader metadata, source URL, tags, etc.
    doc_metadata = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship(
        "Chunk",
        back_populates="document",
        cascade="all, delete-orphan"
    )
