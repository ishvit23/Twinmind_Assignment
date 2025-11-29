import requests
from bs4 import BeautifulSoup
from app.models.document import Document, Chunk, ModalityType
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
from app.services.embedding_service import EmbeddingService

class WebProcessor:
    async def process(self, url: str, user_id: str, db: Session):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {url}") from e

        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else url
        text = soup.get_text(separator="\n", strip=True)

        # Save as document
        doc = Document(
            title=title,
            modality=ModalityType.TEXT,
            source_url=url,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.flush()

        # Chunk text
        chunks = self._create_chunks(text, doc.id)
        db.add_all(chunks)
        db.commit()

        return doc, chunks  # <-- Fix: return tuple, not dict

    def _create_chunks(self, text: str, document_id: str, chunk_size: int = 1000) -> list:
        chunks = []
        chunk_overlap = 200
        text = text.replace('\x00', '').replace('\r', '\n')
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text and len(chunk_text) > 10:
                embedding = EmbeddingService.get_embedding(chunk_text)
                chunk = Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    tokens=len(chunk_text.split()),
                    created_at=datetime.utcnow(),
                    embedding=embedding  # <-- Add this line
                )
                chunks.append(chunk)
        return chunks