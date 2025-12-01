import io
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.ingestion.document_processor import DocumentProcessor
from app.services.ingestion.audio_processor import AudioProcessor
from app.services.ingestion.image_processor import ImageProcessor
from app.services.ingestion.text_processor import TextProcessor
from app.services.ingestion.web_processor import WebProcessor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ingest")

# ------------------------------
# DOCUMENT
# ------------------------------
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    try:
        content = (await file.read()).decode("utf-8", errors="ignore")
        processor = DocumentProcessor()
        doc, chunks = await processor.process(content, file.filename, user_id, db)
        return {"status": "ok", "filename": file.filename}
    except Exception as e:
        logger.error("Document ingestion error", exc_info=True)
        raise HTTPException(500, str(e))


# ------------------------------
# TEXT
# ------------------------------
@router.post("/text")
async def upload_text(data: dict, db: Session = Depends(get_db)):
    try:
        text = data["text"]
        title = data.get("title", "Untitled")
        user_id = data.get("user_id", "default_user")
        doc, chunks = await TextProcessor().process(text, title, user_id, db)
        return {"status": "ok", "title": title}
    except Exception as e:
        logger.error("Text ingestion error", exc_info=True)
        raise HTTPException(500, str(e))
