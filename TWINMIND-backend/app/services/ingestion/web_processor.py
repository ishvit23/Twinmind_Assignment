import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService


class WebProcessor:
    async def process(self, url: str, user_id: str, db: Session):

        # ---------------------------
        # 1. Fetch HTML
        # ---------------------------
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            html = response.text
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {url}") from e

        # ---------------------------
        # 2. Extract title + text
        # ---------------------------
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else url
        text = soup.get_text(separator="\n", strip=True)

        # ---------------------------
        # 3. Create Document
        # ---------------------------
        doc = Document(
            title=title,
            modality=ModalityType.TEXT,
            file_path=None,  # no file path for web
            doc_metadata=f"uploaded_by:{user_id};source_url:{url}",
            created_at=datetime.utcnow()
        )

        db.add(doc)
        db.flush()  # generate doc.id

        # ---------------------------
        # 4. Chunk + embed
        # ---------------------------
        chunks = self._create_chunks(text, doc.id)

        if chunks:
            db.add_all(chunks)
            db.commit()

        return doc, chunks

    # ---------------------------
    # Helper: chunk creator
    # ---------------------------
    def _create_chunks(self, text: str, document_id: str, chunk_size: int = 1000):

        chunks = []
        overlap = 200

        text = text.replace("\x00", "").replace("\r", "\n")

        for i in range(0, len(text), chunk_size - overlap):
            piece = text[i:i + chunk_size].strip()

            if len(piece) > 10:
                emb = EmbeddingService.get_embedding(piece)

                chunk = Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=piece,
                    tokens=len(piece.split()),
                    embedding=emb,
                    created_at=datetime.utcnow()
                )

                chunks.append(chunk)

        return chunks
