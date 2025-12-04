import uuid
import os
import logging
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from PIL import Image
import pytesseract

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Ensure folder exists
os.makedirs("uploads", exist_ok=True)


class ImageProcessor:
    async def process(self, file: UploadFile, user_id: str, db: Session):
        """
        Process image → OCR → chunk → embed → store in DB
        With added debug logging.
        """
        try:
            logger.info(f"[IMG] Starting ingestion for file: {file.filename}")

            # =============================
            # 1️⃣ Save raw image to disk
            # =============================
            image_path = f"uploads/{uuid.uuid4()}_{file.filename}"

            raw_bytes = await file.read()
            with open(image_path, "wb") as f:
                f.write(raw_bytes)

            logger.info(f"[IMG] Saved image at: {image_path} ({len(raw_bytes)} bytes)")

            # =============================
            # 2️⃣ OCR Processing
            # =============================
            try:
                img = Image.open(image_path)
                ocr_text = pytesseract.image_to_string(img)

                logger.info(
                    f"[IMG] OCR extracted {len(ocr_text.strip())} characters. "
                    f"Preview: {repr(ocr_text[:200])}"
                )

            except Exception as e:
                logger.error(f"[IMG] OCR failed: {e}", exc_info=True)
                ocr_text = ""

            # =============================
            # 3️⃣ Insert Document row
            # =============================
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

            logger.info(f"[IMG] Document saved → ID: {doc.id}")

            # =============================
            # 4️⃣ Chunking OCR text
            # =============================
            chunks = []

            if not ocr_text.strip():
                logger.warning(f"[IMG] No OCR text found → No chunks will be created")

            else:
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

                logger.info(f"[IMG] Total chunks generated: {len(chunks)}")

            # =============================
            # 5️⃣ Save Chunks
            # =============================
            if chunks:
                db.add_all(chunks)
                db.commit()
                logger.info(f"[IMG] Saved {len(chunks)} chunks to DB")

            else:
                logger.warning(f"[IMG] No chunks saved (empty OCR text)")

            return doc, chunks

        except Exception as e:
            db.rollback()
            logger.error(f"[IMG] Image ingestion failed: {e}", exc_info=True)
            raise
