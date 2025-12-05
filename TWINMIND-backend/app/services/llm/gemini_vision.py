import google.generativeai as genai
import logging
import mimetypes
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Configure Gemini using the correct env variable
genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiVisionOCR:
    @staticmethod
    def extract_text(image_path: str) -> str:
        """
        Extract readable text from an image using Gemini Vision OCR.
        Supports PNG, JPG, JPEG.
        """
        try:
            # Detect correct MIME type
            mime_type, _ = mimetypes.guess_type(image_path)
            mime_type = mime_type or "image/jpeg"

            with open(image_path, "rb") as f:
                img_bytes = f.read()

            model = genai.GenerativeModel("models/gemini-2.5-pro")

            prompt = "Extract all readable text from this image. Return ONLY the text."

            result = model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime_type,
                        "data": img_bytes
                    }
                ]
            )

            text = result.text or ""
            logger.info(f"[Gemini OCR] Extracted {len(text)} chars")
            return text

        except Exception as e:
            logger.error(f"[Gemini OCR ERROR]: {e}")
            return ""
