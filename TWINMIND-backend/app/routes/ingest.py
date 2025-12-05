from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

from app.database.connection import get_db
from app.services.ingestion.document_processor import DocumentProcessor
from app.services.ingestion.audio_processor import AudioProcessor
from app.services.ingestion.web_processor import WebProcessor
from app.services.ingestion.image_processor import ImageProcessor
from app.services.ingestion.text_processor import TextProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# -------------------------------------------------------
# 📄 DOCUMENT INGESTION
# -------------------------------------------------------
@router.post("/ingest/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Query("demo_user"),
    db: Session = Depends(get_db),
):
    try:
        doc, chunks = await DocumentProcessor().process(file, user_id, db)
        return {
            "status": "success",
            "document_id": str(doc.id),
            "filename": file.filename,
            "chunks_created": len(chunks),
        }
    except Exception as e:
        logger.error("Document upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# 🎵 AUDIO INGESTION
# -------------------------------------------------------
@router.post("/ingest/audio")
async def upload_audio(
    file: UploadFile = File(...),
    user_id: str = Query("demo_user"),
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



# -------------------------------------------------------
# 🌍 WEB INGESTION
# -------------------------------------------------------
class WebIngestRequest(BaseModel):
    url: str
    user_id: str = "demo_user"


@router.post("/ingest/web")
async def upload_web(req: WebIngestRequest, db: Session = Depends(get_db)):
    try:
        doc, chunks = await WebProcessor().process(req.url, req.user_id, db)
        return {
            "status": "success",
            "url": req.url,
            "document_id": str(doc.id),
            "title": doc.title,
            "chunks_created": len(chunks),
        }
    except Exception as e:
        logger.error("Web ingestion failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# 🖼️ IMAGE INGESTION
# -------------------------------------------------------
@router.post("/ingest/image")
async def upload_image(
    file: UploadFile = File(...),
    user_id: str = Query("demo_user"),
    db: Session = Depends(get_db),
):
    try:
        doc, chunks = await ImageProcessor().process(file, user_id, db)
        preview = chunks[0].content[:200] if chunks else ""
        return {
            "status": "success",
            "document_id": str(doc.id),
            "filename": file.filename,
            "ocr_preview": preview,
        }
    except Exception as e:
        logger.error("Image upload failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------------
# ✏️ TEXT INGESTION
# -------------------------------------------------------
class TextUpload(BaseModel):
    text: str
    title: str = "Untitled"
    user_id: str = "demo_user"


@router.post("/ingest/text")
async def upload_text(upload: TextUpload, db: Session = Depends(get_db)):
    try:
        document, chunks = await TextProcessor().process(
            upload.text, upload.title, upload.user_id, db
        )
        return {
            "status": "success",
            "message": "Text processed",
            "document_id": str(document.id),
            "chunks_created": len(chunks),
            "title": document.title,
        }
    except Exception as e:
        logger.error("Text ingestion failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
