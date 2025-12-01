from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.database.connection import SessionLocal
from app.utils.chunking import chunk_text
from app.services.embedding_service import EmbeddingService
from datetime import datetime
import uuid

class TextProcessor:
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def process(self, text: str, title: str, user_id: str):
        """Process plain text input"""
        db = SessionLocal()
        try:
            # Create document record
            doc_id = str(uuid.uuid4())
            document = Document(
                id=doc_id,
                title=title,
                modality=ModalityType.TEXT,
                created_at=datetime.utcnow(),
                doc_metadata=f"uploaded_by:{user_id}"
            )
            db.add(document)
            db.flush()  # Make sure document.id is generated
            
            # Create chunks from text
            chunks = chunk_text(text)

            # Insert chunks with embeddings
            chunk_count = 0
            for idx, chunk_text_content in enumerate(chunks):
                embedding = EmbeddingService.get_embedding(chunk_text_content)

                chunk = Chunk(
                    document_id=document.id,
                    chunk_index=idx,
                    content=chunk_text_content,
                    tokens=len(chunk_text_content.split()),
                    embedding=embedding
                )
                db.add(chunk)
                chunk_count += 1
            
            db.commit()

            return {
                "document_id": doc_id,
                "chunk_count": chunk_count,
                "title": title
            }
        
        finally:
            db.close()
