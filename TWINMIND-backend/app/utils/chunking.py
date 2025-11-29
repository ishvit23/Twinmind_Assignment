from app.config import get_settings

settings = get_settings()

def chunk_text(text: str, chunk_size: int = None, overlap: int = None):
    """
    Split text into overlapping chunks
    """
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if overlap is None:
        overlap = settings.CHUNK_OVERLAP
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start += (chunk_size - overlap)
    
    return chunks