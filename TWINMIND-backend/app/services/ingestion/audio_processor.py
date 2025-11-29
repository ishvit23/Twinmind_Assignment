import whisper
import os
import uuid
from whisper import audio
from app.models.document import Document, Chunk, ModalityType
from datetime import datetime
from app.services.embedding_service import EmbeddingService

# Hard-set FFmpeg paths for Windows
audio.FFMPEG_PATH = r"C:\Users\dhruv\Downloads\ffmpeg-2025-11-27-git-61b034a47c-full_build\ffmpeg-2025-11-27-git-61b034a47c-full_build\bin\ffmpeg.exe"
audio.FFPROBE_PATH = r"C:\Users\dhruv\Downloads\ffmpeg-2025-11-27-git-61b034a47c-full_build\ffmpeg-2025-11-27-git-61b034a47c-full_build\bin\ffprobe.exe"

class AudioProcessor:
    def __init__(self):
        self.model = whisper.load_model("base")  # You can use "tiny" for faster but less accurate

    def process(self, upload_file, user_id="default_user", db=None, *args, **kwargs):
        # Ensure temp directory exists
        temp_dir = "temp_audio"
        os.makedirs(temp_dir, exist_ok=True)

        # Use a unique temp filename to avoid conflicts
        ext = os.path.splitext(upload_file.filename)[-1].lower()
        if ext not in [".mp3", ".wav", ".m4a"]:
            raise ValueError(f"Unsupported audio format: {ext}")

        temp_path = os.path.join(temp_dir, f"{uuid.uuid4().hex}{ext}")
        with open(temp_path, "wb") as f:
            f.write(upload_file.file.read())

        # Double-check file exists before transcription
        if not os.path.exists(temp_path):
            raise FileNotFoundError(f"Temp file not found: {temp_path}")

        # Transcribe audio
        try:
            result = self.model.transcribe(temp_path)
            transcript = result["text"]
        except Exception as e:
            raise RuntimeError(f"Whisper transcription failed: {e}")

        # Create Document entry
        doc = Document(
            title=upload_file.filename,
            modality=ModalityType.AUDIO,
            file_path=temp_path,
            doc_metadata=f"uploaded_by:{user_id}",
            created_at=datetime.utcnow()
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)  # Ensures doc.id is available

        # Chunk transcript and create embeddings
        chunks = self._create_chunks(transcript, doc.id)

        # Delete temp file after all processing
        try:
            os.remove(temp_path)
        except Exception:
            pass  # Ignore errors if file is already deleted

        return doc, chunks

    def _create_chunks(self, text, document_id, chunk_size=1000):
        chunks = []
        chunk_overlap = 200
        for i in range(0, len(text), chunk_size - chunk_overlap):
            chunk_text = text[i:i + chunk_size].strip()
            if chunk_text and len(chunk_text) > 10:
                chunk_text_content = chunk_text
                embedding = EmbeddingService.get_embedding(chunk_text_content)
                chunk = Chunk(
                    document_id=document_id,  # <-- This must not be None
                    chunk_index=len(chunks),
                    content=chunk_text_content,
                    tokens=len(chunk_text_content.split()),
                    embedding=embedding
                )
                chunks.append(chunk)
        return chunks