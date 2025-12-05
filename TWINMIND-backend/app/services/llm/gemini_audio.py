import google.generativeai as genai
from app.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiAudioTranscriber:
    @staticmethod
    def transcribe(audio_bytes: bytes, filename: str) -> str:
        """
        Transcribes audio using Gemini 2.5 pro model.
        Supports mp3 / m4a / wav automatically.
        """
        try:
            model = genai.GenerativeModel("models/gemini-2.5-pro")

            prompt = """
            You are an automatic speech recognition (ASR) system.
            Transcribe ALL spoken words from this audio file.
            Return ONLY raw text without extra commentary.
            """

            mime = "audio/mp3"
            if filename.endswith(".wav"):
                mime = "audio/wav"
            elif filename.endswith(".m4a"):
                mime = "audio/m4a"

            result = model.generate_content(
                [
                    prompt,
                    {
                        "mime_type": mime,
                        "data": audio_bytes
                    }
                ]
            )

            return result.text or ""

        except Exception as e:
            print("[Gemini Audio ERROR]:", e)
            return ""
