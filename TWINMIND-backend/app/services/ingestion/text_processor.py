# app/services/ingestion/text_processor.py

from datetime import datetime
import uuid

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import chunk_text


class TextProcessor:
    def __init__(self):
        pass

    async def process(self, text: str, title: str, user_id: str, db):
        """
        Process plain text, chunk it, embed it, and store in DB.
        Returns (document, chunks_list)
        """

        # Create Document entry
        doc_id = uuid.uuid4()
        document = Document(
            id=doc_id,
            title=title or "Untitled",
            modality=ModalityType.TEXT,
            created_at=datetime.utcnow(),
            doc_metadata=f"uploaded_by:{user_id}"
        )
        db.add(document)
        db.flush()  # ensure ID exists

        # Chunk text
        chunk_texts = chunk_text(text)

        chunks = []
        for idx, chunk_content in enumerate(chunk_texts):
            embedding = EmbeddingService.get_embedding(chunk_content)

            chunk_obj = Chunk(
                document_id=document.id,
                chunk_index=idx,
                content=chunk_content,
                tokens=len(chunk_content.split()),
                embedding=embedding
            )

            db.add(chunk_obj)
            chunks.append(chunk_obj)

        db.commit()
        db.refresh(document)

        return document, chunks
