import os
import uuid
import whisper
from datetime import datetime

from app.models.document import Document, ModalityType
from app.models.chunk import Chunk     # ✅ correct import
from app.services.embedding_service import EmbeddingService


class AudioProcessor:
    def __init__(self):
        # whisper model
        self.model = whisper.load_model("base")

    async def process(self, upload_file, user_id: str, db):
        """
        Process audio upload, transcribe with Whisper, chunk + embed text.
        """

        # -----------------------------------------------------
        # 1. Save audio file temporarily
        # -----------------------------------------------------
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)

        ext = os.path.splitext(upload_file.filename)[1].lower()
        if ext not in [".mp3", ".wav", ".m4a"]:
            raise ValueError(f"Unsupported audio format: {ext}")

        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")

        with open(temp_path, "wb") as f:
            f.write(await upload_file.read())

        # -----------------------------------------------------
        # 2. Whisper transcription
        # -----------------------------------------------------
        try:
            result = self.model.transcribe(temp_path)
            transcript = result.get("text", "").strip()
        except Exception as e:
            raise RuntimeError(f"Whisper transcription failed: {e}")

        # -----------------------------------------------------
        # 3. Create Document entry
        # -----------------------------------------------------
        doc = Document(
            title=upload_file.filename,
            modality=ModalityType.AUDIO,
            file_path=temp_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )

        db.add(doc)
        db.commit()
        db.refresh(doc)

        # -----------------------------------------------------
        # 4. Chunk transcript and embed
        # -----------------------------------------------------
        chunks = self._create_chunks(transcript, doc.id)

        if chunks:
            db.add_all(chunks)
            db.commit()

        # -----------------------------------------------------
        # 5. Cleanup
        # -----------------------------------------------------
        try:
            os.remove(temp_path)
        except:
            pass

        return doc, chunks

    # ---------------------------------------------------------
    # Helper: create chunks with embeddings
    # ---------------------------------------------------------
    def _create_chunks(self, text, document_id, chunk_size=1000):
        chunks = []
        chunk_overlap = 200

        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text and len(chunk_text) > 10:

                embedding = EmbeddingService.get_embedding(chunk_text)

                chunk = Chunk(
                    document_id=document_id,
                    chunk_index=len(chunks),
                    content=chunk_text,
                    tokens=len(chunk_text.split()),
                    embedding=embedding,
                    created_at=datetime.utcnow()
                )
                chunks.append(chunk)

        return chunks
