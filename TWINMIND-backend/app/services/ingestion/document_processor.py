from fastapi import UploadFile
import logging
import os
from sqlalchemy.orm import Session
import uuid
import pypdf
from datetime import datetime

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process(self, file: UploadFile, user_id: str, db: Session):
        """
        Process uploaded file and save to database
        """
        try:
            logger.info(f"Processing file: {file.filename}")
            
            # Read file content
            content = await file.read()
            
            # Extract text based on file type
            text = await self._extract_text(file.filename, content)
            
            if not text or len(text.strip()) == 0:
                raise ValueError("No text extracted from file")
            
            # Create document
            doc = Document(
                title=file.filename,
                modality=self._get_modality(file.filename),
                file_path="path/to/file",
                doc_metadata=f"uploaded_by:{user_id}",
                created_at=datetime.utcnow()
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            # Create chunks
            chunks = self._create_chunks(text, doc.id, self.chunk_size)
            db.add_all(chunks)
            db.commit()
            
            logger.info(f"Document processed: {doc.id} with {len(chunks)} chunks")
            
            return doc, chunks

        except Exception as e:
            db.rollback()
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            raise
    
    async def _extract_text(self, filename: str, content: bytes) -> str:
        ext = os.path.splitext(filename)[1].lower()
        
        try:
            if ext == '.pdf':
                return self._extract_pdf_text(content)
            elif ext in ['.txt', '.md']:
                return content.decode('utf-8', errors='ignore')
            else:
                return content.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return ""
    
    def _extract_pdf_text(self, content: bytes) -> str:
        try:
            import io
            pdf_file = io.BytesIO(content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            return ""
    
    def _get_modality(self, filename: str) -> ModalityType:
        ext = os.path.splitext(filename)[1].lower()
        
        if ext == '.pdf':
            return ModalityType.PDF
        elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return ModalityType.IMAGE
        elif ext in ['.mp3', '.wav', '.m4a']:
            return ModalityType.AUDIO
        elif ext in ['.mp4', '.avi', '.mov']:
            return ModalityType.VIDEO
        else:
            return ModalityType.TEXT
    
    def _create_chunks(self, text: str, document_id: str, chunk_size: int = 1000) -> list:
        chunks = []
        overlap = 200
        text = text.replace('\x00', '').replace('\r', '\n')

        for i in range(0, len(text), chunk_size - overlap):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text and len(chunk_text) > 10:

                embedding = EmbeddingService.get_embedding(chunk_text)

                chunk = Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    tokens=len(chunk_text.split()),
                    embedding=embedding
                )
                chunks.append(chunk)

        return chunks
