import google.generativeai as genai
from app.config import get_settings
import base64

settings = get_settings()

# Configure API
genai.configure(api_key=settings.GOOGLE_API_KEY)

class GeminiVisionOCR:
    @staticmethod
    def extract_text(image_path: str) -> str:
        """
        Sends an image to Gemini 1.5 Flash (Vision)
        and extracts the text using OCR-like prompting.
        """
        try:
            with open(image_path, "rb") as f:
                img_bytes = f.read()

            img_base64 = base64.b64encode(img_bytes).decode()

            model = genai.GenerativeModel("gemini-1.5-flash")

            prompt = """
            Extract all readable text from this image.
            Return ONLY the extracted text, no explanation.
            """

            result = model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": "image/png",
                        "data": img_base64
                    }
                ]
            )

            return result.text or ""
        
        except Exception as e:
            print("[Gemini OCR ERROR]:", e)
            return ""
