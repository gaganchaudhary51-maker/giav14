from urllib.parse import urlencode

from backend.config import settings


class TTSService:
    async def fetch_pcm_stream_endpoint(self, text: str) -> str | None:
        if not settings.kokoro_tts_url:
            return None
        # This builds a provider URL; it does not prove the endpoint is reachable
        # and does not itself synthesize or download audio.
        separator = "&" if "?" in settings.kokoro_tts_url else "?"
        query = urlencode({"input": text, "voice": "af_heart", "response_format": "wav"})
        return f"{settings.kokoro_tts_url}{separator}{query}"


tts_service = TTSService()
