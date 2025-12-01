# app/services/ingestion/text_processor.py
from app.models.document import Document, Chunk, ModalityType
from app.database.connection import SessionLocal
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import chunk_text
from datetime import datetime
import uuid

class TextProcessor:
    def __init__(self):
        pass

    async def process(self, text: str, title: str, user_id: str, db):
        """
        Process plain text input and persist to DB.
        Returns (document, chunks_list)
        """
        # create document
        doc_id = uuid.uuid4()
        document = Document(
            id=doc_id,
            title=title or "Untitled",
            modality=ModalityType.TEXT,
            created_at=datetime.utcnow(),
            doc_metadata=f"uploaded_by:{user_id}"
        )
        db.add(document)
        db.flush()  # ensure id present

        # chunk text (use your util)
        chunks_texts = chunk_text(text)

        chunks = []
        for idx, chunk_text_content in enumerate(chunks_texts):
            emb = EmbeddingService.get_embedding(chunk_text_content)
            chunk = Chunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk_text_content,
                tokens=len(chunk_text_content.split()),
                embedding=emb
            )
            db.add(chunk)
            chunks.append(chunk)

        db.commit()
        # refresh
        db.refresh(document)
        return document, chunks
