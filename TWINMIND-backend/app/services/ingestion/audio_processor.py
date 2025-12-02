# app/services/ingestion/audio_processor.py

import uuid
import os
from datetime import datetime
from sqlalchemy.orm import Session
import whisper

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

# Load Whisper ONCE (important for Render)
whisper_model = whisper.load_model("base")


class AudioProcessor:

    async def process(self, file, user_id: str, db: Session):

        # --------------------------------------
        # SAVE FILE
        # --------------------------------------
        audio_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        with open(audio_path, "wb") as f:
            f.write(await file.read())

        # --------------------------------------
        # TRANSCRIBE
        # --------------------------------------
        try:
            result = whisper_model.transcribe(audio_path)
            transcript = result.get("text", "").strip()
        except Exception:
            transcript = ""

        # If empty transcript → provide fallback
        if not transcript:
            transcript = "Transcription failed or audio was silent."

        # --------------------------------------
        # CREATE DOCUMENT RECORD
        # --------------------------------------
        doc = Document(
            title=file.filename,
            modality=ModalityType.AUDIO,
            file_path=audio_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )

        db.add(doc)
        db.flush()

        # --------------------------------------
        # CREATE CHUNKS + EMBEDDINGS
        # --------------------------------------
        chunks = []

        chunk_size = 700
        overlap = 150

        for i in range(0, len(transcript), chunk_size - overlap):
            piece = transcript[i:i + chunk_size].strip()
            if len(piece) < 10:
                continue

            embedding = EmbeddingService.get_embedding(piece)

            # If embedding failed, skip this chunk
            if embedding is None or len(embedding) != EmbeddingService.get_dim():
                continue

            chunk = Chunk(
                document_id=doc.id,
                chunk_index=len(chunks),
                content=piece,
                tokens=len(piece.split()),
                embedding=embedding,
                created_at=datetime.utcnow()
            )

            chunks.append(chunk)

        # Guarantee at least ONE chunk
        if not chunks:
            fallback_text = "No transcript chunks could be generated."
            embedding = EmbeddingService.get_embedding(fallback_text)

            chunk = Chunk(
                document_id=doc.id,
                chunk_index=0,
                content=fallback_text,
                tokens=len(fallback_text.split()),
                embedding=embedding,
                created_at=datetime.utcnow()
            )
            chunks.append(chunk)

        db.add_all(chunks)
        db.commit()

        return doc, chunks
