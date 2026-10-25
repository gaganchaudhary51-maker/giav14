from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers.voice_webhook import router as voice_router
from backend.services.pod_scheduler import start_pod_scheduler, stop_pod_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    stop_event, scheduled_tasks = await start_pod_scheduler()
    app.state.pod_scheduler_stop = stop_event
    app.state.pod_scheduler_tasks = scheduled_tasks
    try:
        yield
    finally:
        await stop_pod_scheduler(stop_event, scheduled_tasks)

app = FastAPI(
    lifespan=lifespan,
    title="HRGEN AI Agents — Voice Integration",
    description="Configurable voice webhook with explicit provider and latency status.",
    version="2026.1.1",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(voice_router)


@app.get("/health")
async def health_check() -> dict[str, object]:
    return {
        "status": "online",
        "service": "hrgen-voice-integration",
        "providers_configured": {
            "groq_stt": bool(settings.groq_api_key),
            "gemini_llm": bool(settings.gemini_api_key),
            "kokoro_tts": bool(settings.kokoro_tts_url),
        },
        "telephony_connected": False,
        "latency_sla_verified": False,
        "pod_scheduler_enabled": settings.pod_scheduler_enabled,
        "pod_scheduler_configured": bool(settings.pod_job_webhook_url and settings.pod_job_webhook_token),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
