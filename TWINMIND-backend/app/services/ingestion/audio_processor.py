import uuid
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService
from app.services.llm.gemini_audio import GeminiAudioTranscriber


class AudioProcessor:

    async def process(self, file, user_id: str, db: Session):
        """
        Audio ingestion using Gemini Flash transcription.
        """

        # ----------------------
        # 1️⃣ Read file bytes
        # ----------------------
        audio_bytes = await file.read()
        audio_path = f"uploads/{uuid.uuid4()}_{file.filename}"

        # Save raw file
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        # ----------------------
        # 2️⃣ Transcribe audio
        # ----------------------
        transcript = GeminiAudioTranscriber.transcribe(
            audio_bytes=audio_bytes, 
            filename=file.filename
        )

        if not transcript.strip():
            transcript = "No speech detected or transcription failed."

        # ----------------------
        # 3️⃣ Create Document entry
        # ----------------------
        doc = Document(
            title=file.filename,
            modality=ModalityType.AUDIO,
            file_path=audio_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.flush()

        # ----------------------
        # 4️⃣ Create Chunk with embedding
        # ----------------------
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
