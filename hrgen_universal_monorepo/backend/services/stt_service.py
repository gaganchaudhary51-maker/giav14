from groq import AsyncGroq

from backend.config import settings


class STTService:
    def __init__(self) -> None:
        self.client = AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    async def transcribe_audio_bytes(self, audio_bytes: bytes, filename: str = "input.wav") -> str:
        if not audio_bytes:
            raise ValueError("Audio upload is empty.")
        if self.client is None:
            raise RuntimeError("Groq STT is not configured; set GROQ_API_KEY.")
        result = await self.client.audio.transcriptions.create(
            file=(filename, audio_bytes),
            model=settings.groq_stt_model,
            response_format="json",
        )
        text = getattr(result, "text", "")
        if not text.strip():
            raise RuntimeError("STT provider returned an empty transcript.")
        return text.strip()


stt_service = STTService()
