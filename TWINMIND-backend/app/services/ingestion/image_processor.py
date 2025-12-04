import uuid
import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from PIL import Image
import pytesseract
import logging

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)


class ImageProcessor:
    async def process(self, file: UploadFile, user_id: str, db: Session):
        """
        Process uploaded image → OCR → chunk → embed → store
        """
        try:
            # ---- Save File ----
            image_path = f"uploads/{uuid.uuid4()}_{file.filename}"
            raw = await file.read()
            with open(image_path, "wb") as f:
                f.write(raw)

            # ---- OCR Processing ----
            try:
                img = Image.open(image_path)
                ocr_text = pytesseract.image_to_string(img)
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")
                ocr_text = ""

            # ---- Store Document ----
            doc = Document(
                title=file.filename,
                modality=ModalityType.IMAGE,
                file_path=image_path,
                doc_metadata=f"uploaded_by:{user_id}",
                created_at=datetime.utcnow(),
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # ---- Chunk OCR text ----
            chunks = []

            if ocr_text.strip():
                chunk_size = 1000
                overlap = 200

                clean_text = ocr_text.replace("\x00", "").replace("\r", "\n")

                for i in range(0, len(clean_text), chunk_size - overlap):
                    chunk_text = clean_text[i : i + chunk_size].strip()

                    if chunk_text and len(chunk_text) > 10:
                        embedding = EmbeddingService.get_embedding(chunk_text)

                        chunk = Chunk(
                            document_id=doc.id,
                            chunk_index=len(chunks),
                            content=chunk_text,
                            tokens=len(chunk_text.split()),
                            embedding=embedding,
                        )
                        chunks.append(chunk)

            # ---- Save Chunks ----
            if chunks:
                db.add_all(chunks)
                db.commit()

            logger.info(f"Image processed → {len(chunks)} chunks created")
            return doc, chunks

        except Exception as e:
            db.rollback()
            logger.error(f"Image ingestion failed: {e}", exc_info=True)
            raise
