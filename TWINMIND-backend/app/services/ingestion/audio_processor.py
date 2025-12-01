from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import whisper

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk
from app.services.embedding_service import EmbeddingService

class AudioProcessor:
    async def process(self, file, user_id: str, db: Session):

        audio_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        with open(audio_path, "wb") as f:
            f.write(await file.read())

        model = whisper.load_model("base")
        result = model.transcribe(audio_path)

        transcript = result.get("text", "").strip()

        doc = Document(
            title=file.filename,
            modality=ModalityType.AUDIO,
            file_path=audio_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        chunks = []
        if transcript:
            chunk_size = 1000
            overlap = 200

            for i in range(0, len(transcript), chunk_size - overlap):
                piece = transcript[i:i + chunk_size].strip()
                if len(piece) < 10:
                    continue

                emb = EmbeddingService.get_embedding(piece)

                chunk = Chunk(
                    document_id=doc.id,
                    chunk_index=len(chunks),
                    content=piece,
                    tokens=len(piece.split()),
                    embedding=emb
                )
                chunks.append(chunk)

            db.add_all(chunks)
            db.commit()

        return doc, chunks
