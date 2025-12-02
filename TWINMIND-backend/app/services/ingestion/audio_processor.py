# app/services/ingestion/audio_processor.py

import uuid
import os
from datetime import datetime
from sqlalchemy.orm import Session

from openai import OpenAI
client = OpenAI()

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService


class AudioProcessor:

    async def process(self, file, user_id: str, db: Session):

        # --------------------------------------
        # SAVE FILE
        # --------------------------------------
        os.makedirs("uploads", exist_ok=True)
        audio_path = f"uploads/{uuid.uuid4()}_{file.filename}"

        with open(audio_path, "wb") as f:
            f.write(await file.read())

        # --------------------------------------
        # TRANSCRIBE USING WHISPER API
        # --------------------------------------
        try:
            with open(audio_path, "rb") as audio_file:
                result = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            transcript = (result.text or "").strip()

        except Exception:
            transcript = ""

        if not transcript:
            transcript = "Transcription failed or audio was silent."

        # --------------------------------------
        # CREATE DOCUMENT
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
        # CREATE CHUNKS WITH EMBEDDINGS
        # --------------------------------------
        chunks = []
        chunk_size = 700
        overlap = 150

        for i in range(0, len(transcript), chunk_size - overlap):

            piece = transcript[i:i + chunk_size].strip()
            if len(piece) < 10:
                continue

            emb = EmbeddingService.get_embedding(piece)

            if not emb:
                continue

            chunk = Chunk(
                document_id=doc.id,
                chunk_index=len(chunks),
                content=piece,
                tokens=len(piece.split()),
                embedding=emb,
                created_at=datetime.utcnow()
            )
            chunks.append(chunk)

        if not chunks:
            text = "No transcript chunks could be generated."
            emb = EmbeddingService.get_embedding(text)

            chunk = Chunk(
                document_id=doc.id,
                chunk_index=0,
                content=text,
                tokens=len(text.split()),
                embedding=emb,
                created_at=datetime.utcnow()
            )
            chunks.append(chunk)

        db.add_all(chunks)
        db.commit()

        return doc, chunks
