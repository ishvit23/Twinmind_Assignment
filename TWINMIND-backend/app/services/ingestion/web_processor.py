import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk     #Correct import
from app.services.embedding_service import EmbeddingService


class WebProcessor:
    async def process(self, url: str, user_id: str, db: Session):
        """Fetch webpage, extract text, chunk, embed, and store."""
        # ----------------------------------------------------
        # 1. Fetch HTML
        # ----------------------------------------------------
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {url}") from e

        # ----------------------------------------------------
        # 2. Extract text + title
        # ----------------------------------------------------
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else url
        text = soup.get_text(separator="\n", strip=True)

        # ----------------------------------------------------
        # 3. Create Document entry
        # ----------------------------------------------------
        doc = Document(
            title=title,
            modality=ModalityType.TEXT,  # Web → treated as TEXT
            source_url=url,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.flush()   # ensure doc.id exists

        # ----------------------------------------------------
        # 4. Chunk the text and generate embeddings
        # ----------------------------------------------------
        chunks = self._create_chunks(text, doc.id)

        if chunks:
            db.add_all(chunks)
            db.commit()

        return doc, chunks   # Always return tuple

    # --------------------------------------------------------
    # Helper: Chunk creator
    # --------------------------------------------------------
    def _create_chunks(self, text: str, document_id: str, chunk_size: int = 1000) -> list:
        chunks = []
        chunk_overlap = 200

        text = text.replace("\x00", "").replace("\r", "\n")

        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size].strip()

            if chunk_text and len(chunk_text) > 10:
                embedding = EmbeddingService.get_embedding(chunk_text)

                chunk = Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    tokens=len(chunk_text.split()),
                    embedding=embedding,
                    created_at=datetime.utcnow()
                )

                chunks.append(chunk)

        return chunks
