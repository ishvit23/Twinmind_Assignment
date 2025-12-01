from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from sqlalchemy.orm import Session
import logging

from app.database.connection import get_db

# Correct imports
from app.models.document import Document
from app.models.chunk import Chunk

from app.services.ingestion.document_processor import DocumentProcessor
from app.services.ingestion.audio_processor import AudioProcessor
from app.services.ingestion.web_processor import WebProcessor
from app.services.ingestion.image_processor import ImageProcessor
from app.services.ingestion.text_processor import TextProcessor
from pydantic import BaseModel


logger = logging.getLogger(__name__)
router = APIRouter()


# --------------------------------------------------------------------------
# UPLOAD PDF / DOC
# --------------------------------------------------------------------------
@router.post("/ingest/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    try:
        processor = DocumentProcessor()
        doc, chunks = await processor.process(file, user_id, db)

        return {
            "status": "success",
            "document_id": doc.id,
            "filename": file.filename,
            "chunks_created": len(chunks)
        }

    except Exception as e:
        logger.error("Upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# LIST DOCUMENTS
# --------------------------------------------------------------------------
@router.get("/documents")
async def list_documents(db: Session = Depends(get_db)):
    try:
        docs = db.query(Document).all()
        return {
            "status": "success",
            "count": len(docs),
            "documents": [
                {
                    "id": d.id,
                    "title": d.title,
                    "modality": d.modality.value,
                    "created_at": d.created_at,
                    "chunks_count": len(d.chunks)
                }
                for d in docs
            ]
        }

    except Exception as e:
        logger.error("List documents failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# GET SINGLE DOCUMENT
# --------------------------------------------------------------------------
@router.get("/documents/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        chunks = db.query(Chunk).filter(Chunk.document_id == document_id).all()

        return {
            "status": "success",
            "document": {
                "id": doc.id,
                "title": doc.title,
                "modality": doc.modality.value,
                "created_at": doc.created_at,
                "chunks_count": len(chunks),
            },
            "chunks": [
                {
                    "id": c.id,
                    "index": c.chunk_index,
                    "content": c.content[:200] + "..." if len(c.content) > 200 else c.content,
                }
                for c in chunks
            ]
        }

    except Exception as e:
        logger.error("Get document failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# DELETE DOCUMENT
# --------------------------------------------------------------------------
@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        db.delete(doc)
        db.commit()

        return {"status": "success", "message": "Document deleted"}

    except Exception as e:
        logger.error("Delete failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# AUDIO INGESTION
# --------------------------------------------------------------------------
@router.post("/ingest/audio")
async def upload_audio(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    try:
        doc, chunks = await AudioProcessor().process(file, user_id, db)

        return {
            "status": "success",
            "document_id": doc.id,
            "filename": file.filename,
            "transcript_sample": chunks[0].content[:200] if chunks else ""
        }

    except Exception as e:
        logger.error("Audio upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# WEB INGESTION
# --------------------------------------------------------------------------
class WebIngestRequest(BaseModel):
    url: str
    user_id: str = "default_user"


@router.post("/ingest/web")
async def upload_web(req: WebIngestRequest, db: Session = Depends(get_db)):
    try:
        doc, chunks = await WebProcessor().process(req.url, req.user_id, db)

        return {
            "status": "success",
            "url": req.url,
            "document_id": doc.id,
            "title": doc.title,
            "chunks_created": len(chunks)
        }

    except Exception as e:
        logger.error("Web upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# IMAGE INGESTION
# --------------------------------------------------------------------------
@router.post("/ingest/image")
async def upload_image(file: UploadFile = File(...), user_id: str = "default_user", db: Session = Depends(get_db)):
    try:
        doc, chunks = await ImageProcessor().process(file, user_id, db)

        return {
            "status": "success",
            "document_id": doc.id,
            "filename": file.filename,
            "ocr_preview": chunks[0].content[:200] if chunks else "",
        }

    except Exception as e:
        logger.error("Image upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# --------------------------------------------------------------------------
# TEXT INGESTION
# --------------------------------------------------------------------------
class TextUpload(BaseModel):
    text: str
    title: str = "Untitled"
    user_id: str = "default_user"


@router.post("/ingest/text")
async def upload_text(req: TextUpload, db: Session = Depends(get_db)):
    try:
        doc, chunks = await TextProcessor().process(req.text, req.title, req.user_id, db)

        return {
            "status": "success",
            "document_id": doc.id,
            "chunks_created": len(chunks),
            "title": req.title
        }

    except Exception as e:
        logger.error("Text upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
