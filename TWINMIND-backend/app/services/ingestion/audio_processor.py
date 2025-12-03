# app/services/ingestion/audio_processor.py

import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService


class AudioProcessor:

    async def process(self, file, user_id: str, db: Session):
        """
        Whisper disabled to avoid OOM. We store a fallback transcript instead.
        """

        # Save file (optional—you can disable saving too)
        audio_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        with open(audio_path, "wb") as f:
            f.write(await file.read())

        # Fallback transcript
        transcript = "Audio transcription temporarily disabled due to memory limits."

        # Create Document record
        doc = Document(
            title=file.filename,
            modality=ModalityType.AUDIO,
            file_path=audio_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )

        db.add(doc)
        db.flush()

        # Create one fallback chunk
        embedding = EmbeddingService.get_embedding(transcript)

        chunk = Chunk(
            document_id=doc.id,
            chunk_index=0,
            content=transcript,
            tokens=len(transcript.split()),
            embedding=embedding,
            created_at=datetime.utcnow()
        )

        db.add(chunk)
        db.commit()

        return doc, [chunk]
