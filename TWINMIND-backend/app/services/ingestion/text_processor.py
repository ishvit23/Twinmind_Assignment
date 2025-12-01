from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

class TextProcessor:
    async def process(self, text: str, title: str, user_id: str, db: Session):
        # Create the document
        doc = Document(
            title=title,
            modality=ModalityType.TEXT,
            file_path=None,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        # Chunk logic
        chunks = []
        chunk_size = 1000
        overlap = 200

        for i in range(0, len(text), chunk_size - overlap):
            piece = text[i:i + chunk_size].strip()
            if not piece:
                continue

            emb = EmbeddingService.get_embedding(piece)

            chunk = Chunk(
                document_id=doc.id,
                chunk_index=len(chunks),
                content=piece,
                tokens=len(piece.split()),
                embedding=emb
            )
            chunks.append(chunk)

        if chunks:
            db.add_all(chunks)
            db.commit()

        return doc, chunks
