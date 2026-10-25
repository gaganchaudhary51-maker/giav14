from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str = ""
    gemini_api_key: str = ""
    groq_stt_model: str = "whisper-large-v3"
    gemini_llm_model: str = "gemini-2.5-flash"
    kokoro_tts_url: str = "http://127.0.0.1:8888/v1/audio/tts"
    voice_webhook_token: str = ""
    app_env: str = "development"
    pod_scheduler_enabled: bool = False
    pod_job_webhook_url: str = ""
    pod_job_webhook_token: str = ""
    swarn_auditor_interval_seconds: int = 3600
    lucas_growth_interval_seconds: int = 21600
    swarn_auditor_prompt: str = "Review configured operational audit signals and return a concise findings summary."
    lucas_growth_prompt: str = "Review configured growth signals and return a concise experiment and content-opportunity summary."
    cors_allow_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()
