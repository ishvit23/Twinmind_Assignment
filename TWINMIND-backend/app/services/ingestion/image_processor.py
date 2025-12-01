from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os
from PIL import Image
import pytesseract

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

class ImageProcessor:
    async def process(self, file: UploadFile, user_id: str, db: Session):
        # Save image file
        image_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        with open(image_path, "wb") as f:
            f.write(await file.read())

        # OCR extraction
        try:
            img = Image.open(image_path)
            ocr_text = pytesseract.image_to_string(img)
        except Exception:
            ocr_text = ""
        
        # Create Document
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

        # Chunk creation
        chunks = []
        if ocr_text.strip():
            chunk_size = 1000
            overlap = 200
            text = ocr_text.replace('\x00', '').replace('\r', '\n')

            for i in range(0, len(text), chunk_size - overlap):
                chunk_text = text[i:i + chunk_size].strip()
                if chunk_text and len(chunk_text) > 10:
                    embedding = EmbeddingService.get_embedding(chunk_text)

                    chunk = Chunk(
                        document_id=doc.id,
                        chunk_index=len(chunks),
                        content=chunk_text,
                        tokens=len(chunk_text.split()),
                        embedding=embedding
                    )
                    chunks.append(chunk)

        if chunks:
            db.add_all(chunks)
            db.commit()

        return doc, chunks


async def process_image(file: UploadFile, user_id: str, db: Session):
    image_path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(image_path, "wb") as f:
        f.write(await file.read())

    # OCR extraction
    try:
        img = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(img)
    except Exception:
        ocr_text = ""
    
    # Document
    doc = Document(
        title=file.filename,
        modality=ModalityType.IMAGE,
        file_path=image_path,
        doc_metadata=f"uploaded_by:{user_id}",
        created_at=datetime.utcnow()
    )

    # Chunk generation (if OCR text exists)
    chunks = []
    if ocr_text.strip():
        chunk_size = 1000
        overlap = 200
        text = ocr_text.replace('\x00', '').replace('\r', '\n')

        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text and len(chunk_text) > 10:
                embedding = EmbeddingService.get_embedding(chunk_text)

                chunk = Chunk(
                    document_id=doc.id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    tokens=len(chunk_text.split()),
                    embedding=embedding
                )
                chunks.append(chunk)

    return doc, chunks
