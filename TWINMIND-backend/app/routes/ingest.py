from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Body
from sqlalchemy.orm import Session
import logging
from app.services.ingestion.document_processor import DocumentProcessor
from app.services.ingestion.audio_processor import AudioProcessor
from app.services.ingestion.web_processor import WebProcessor
from app.services.ingestion.image_processor import ImageProcessor
from app.services.ingestion.text_processor import TextProcessor
from app.database.connection import get_db
from app.models.document import Document, Chunk
from pydantic import BaseModel
from urllib.parse import urlparse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ingest/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Upload and process a file (PDF, MD, Audio, etc.)"""
    try:
        logger.info(f"Uploading file: {file.filename} for user: {user_id}")
        processor = DocumentProcessor()
        result = await processor.process(file, user_id, db)
        doc, chunks = result
        return {
            "status": "success",
            "message": "Document uploaded and processed",
            "filename": file.filename,
            "user_id": user_id,
            "document_id": doc.id,
            "chunks_created": len(chunks)
        }
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def list_documents(user_id: str = "default_user", db: Session = Depends(get_db)):
    """Get a list of all documents"""
    try:
        documents = db.query(Document).all()
        return {
            "status": "success",
            "count": len(documents),
            "documents": [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "modality": doc.modality,
                    "created_at": doc.created_at,
                    "chunks_count": len(doc.chunks)
                }
                for doc in documents
            ]
        }
    except Exception as e:
        logger.error(f"List documents failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents/{document_id}")
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a specific document"""
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
                "modality": doc.modality,
                "created_at": doc.created_at,
                "chunks_count": len(chunks)
            },
            "chunks": [
                {
                    "id": chunk.id,
                    "index": chunk.chunk_index,
                    "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "tokens": chunk.tokens
                }
                for chunk in chunks
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/documents/{document_id}")
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document"""
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        db.delete(doc)
        db.commit()
        return {"status": "success", "message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest/audio")
async def upload_audio(file: UploadFile = File(...), user_id: str = "default_user", db: Session = Depends(get_db)):
    """Upload and process an audio file"""
    try:
        document, chunks = AudioProcessor().process(file, user_id, db=db)
        db.add(document)
        for chunk in chunks:
            db.add(chunk)
        db.commit()
        return {
            "status": "success",
            "filename": file.filename,
            "user_id": user_id,
            "document_id": document.id,
            "transcript": chunks[0].content if chunks else ""
        }
    except Exception as e:
        logging.error(f"Audio upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Audio upload failed: {e}")

class WebIngestRequest(BaseModel):
    url: str
    user_id: str = "default_user"

@router.post("/ingest/web")
async def upload_web(json: dict, db: Session = Depends(get_db)):
    try:
        url = json["url"]
        user_id = json.get("user_id", "default_user")
        document, chunks = await WebProcessor().process(url, user_id, db)
        db.add(document)
        for chunk in chunks:
            db.add(chunk)
        db.commit()
        return {
            "status": "success",
            "url": url,
            "user_id": user_id,
            "document_id": document.id,
            "title": document.title,
            "text_length": sum(len(chunk.content) for chunk in chunks)
        }
    except Exception as e:
        logging.error(f"Web upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Web upload failed: {e}")

@router.post("/ingest/image")
async def upload_image(file: UploadFile = File(...), user_id: str = "default_user", db: Session = Depends(get_db)):
    try:
        document, chunks = await ImageProcessor().process(file, user_id, db)
        db.add(document)
        for chunk in chunks:
            db.add(chunk)
        db.commit()
        return {
            "status": "success",
            "filename": file.filename,
            "user_id": user_id,
            "document_id": document.id,
            "ocr_text": chunks[0].content if chunks else "",
            "image_path": document.file_path
        }
    except Exception as e:
        logging.error(f"Image upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Image upload failed: {e}")

@router.post("/ingest/document")
async def upload_document_alias(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    return await upload_document(file, user_id, db)

@router.post("/ingest/text")
async def upload_text(
    text: str = Body(...),
    title: str = Body("Untitled"),
    user_id: str = Body("default_user")
):
    try:
        processor = TextProcessor()
        result = await processor.process(text, title, user_id)
        doc, chunks = result  # unpack the tuple
        return {
            "status": "success",
            "message": "Text uploaded and processed",
            "document_id": doc.id,
            "chunks_created": len(chunks),
            "title": title
        }
    except Exception as e:
        logger.error(f"Text upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Text upload failed: {e}")