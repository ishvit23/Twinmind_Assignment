import uuid
import os
import logging
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService
from app.services.llm.gemini_vision import GeminiVisionOCR

logger = logging.getLogger(__name__)

# Ensure folder exists
os.makedirs("uploads", exist_ok=True)


class ImageProcessor:
    async def process(self, file: UploadFile, user_id: str, db: Session):
        try:
            # -------------------
            # 1️⃣ Save raw image
            # -------------------
            image_path = f"uploads/{uuid.uuid4()}_{file.filename}"
            raw = await file.read()
            with open(image_path, "wb") as f:
                f.write(raw)

            # -------------------
            # 2️⃣ Gemini Vision OCR
            # -------------------
            ocr_text = GeminiVisionOCR.extract_text(image_path)
            logger.info(f"[IMG] Gemini OCR extracted {len(ocr_text)} chars")

            # -------------------
            # 3️⃣ Create Document
            # -------------------
            doc = Document(
                title=file.filename,
                modality=ModalityType.IMAGE,
                file_path=image_path,
                doc_metadata=f"uploaded_by:{user_id}",
                created_at=datetime.utcnow()
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # -------------------
            # 4️⃣ Chunk OCR text
            # -------------------
            chunks = []
            if ocr_text.strip():
                chunk_size = 1000
                overlap = 200
                clean = ocr_text.replace("\x00", "").replace("\r", "\n")

                for i in range(0, len(clean), chunk_size - overlap):
                    chunk_text = clean[i:i + chunk_size].strip()
                    if len(chunk_text) > 10:
                        embedding = EmbeddingService.get_embedding(chunk_text)

                        chunk = Chunk(
                            document_id=doc.id,
                            chunk_index=len(chunks),
                            content=chunk_text,
                            tokens=len(chunk_text.split()),
                            embedding=embedding,
                        )
                        chunks.append(chunk)

            if chunks:
                db.add_all(chunks)
                db.commit()
                logger.info(f"[IMG] Saved {len(chunks)} OCR chunks")

            else:
                logger.warning("[IMG] No text extracted → no chunks saved")

            return doc, chunks

        except Exception as e:
            db.rollback()
            logger.error("[IMG] Error during image processing", exc_info=True)
            raise
