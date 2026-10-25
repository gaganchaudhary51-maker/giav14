from google import genai

from backend.config import settings


class LLMService:
    def __init__(self) -> None:
        self.client = genai.Client(api_key=settings.gemini_api_key) if settings.gemini_api_key else None

    async def generate_voice_response(self, system_persona_prompt: str, user_input_text: str) -> str:
        if self.client is None:
            raise RuntimeError("Gemini LLM is not configured; set GEMINI_API_KEY.")
        if not user_input_text.strip():
            raise ValueError("Transcript is empty.")
        response = await self.client.aio.models.generate_content(
            model=settings.gemini_llm_model,
            contents=f"Caller transcript:\n{user_input_text}",
            config={
                "system_instruction": (
                    f"{system_persona_prompt}\n"
                    "Answer briefly, safely, and in plain language. Aim for at most 18 words. "
                    "Do not claim to have booked, transferred, or completed an action unless a tool confirms it."
                ),
                "max_output_tokens": 120,
                "temperature": 0.2,
            },
        )
        text = (response.text or "").strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response.")
        words = text.split()
        if len(words) > 20:
            text = " ".join(words[:18]).rstrip(" ,;:") + "."
        return text


llm_service = LLMService()
