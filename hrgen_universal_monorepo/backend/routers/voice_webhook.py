import time
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, HTTPException, UploadFile
from fastapi import status

from backend.config import settings
from backend.schemas.voice import ActionType, VoiceActionResponse
from backend.security import verify_voice_webhook_auth
from backend.services.handover_service import handover_service
from backend.services.llm_service import llm_service
from backend.services.stt_service import stt_service
from backend.services.tts_service import tts_service

router = APIRouter(prefix="/api/voice", tags=["Voice Telephony Webhook"])


async def require_webhook_auth(authorization: Annotated[str | None, Header()] = None) -> None:
    # Fail closed in production by setting VOICE_WEBHOOK_TOKEN.
    verify_voice_webhook_auth(authorization, settings.voice_webhook_token, settings.app_env)


@router.post("/webhook", response_model=VoiceActionResponse, dependencies=[Depends(require_webhook_auth)])
async def process_telephony_ingestion(
    background_tasks: BackgroundTasks,
    call_id: Annotated[str, Form(min_length=1, max_length=128)],
    caller_id: Annotated[str, Form(min_length=1, max_length=128)],
    agent_pod_id: Annotated[str, Form(min_length=1, max_length=80)],
    transcript: Annotated[str | None, Form(max_length=12000)] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> VoiceActionResponse:
    started = time.perf_counter()
    if file is not None:
        # Read at most limit + 1 byte so an oversized upload is not fully buffered.
        raw_audio = await file.read((15 * 1024 * 1024) + 1)
        if len(raw_audio) > 15 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="Audio upload exceeds 15 MiB limit")
        try:
            runtime_transcript = await stt_service.transcribe_audio_bytes(raw_audio, file.filename or "input.wav")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail="Speech transcription provider failed") from exc
    elif transcript and transcript.strip():
        runtime_transcript = transcript.strip()
    else:
        raise HTTPException(status_code=400, detail="Provide a non-empty transcript or audio file")

    if handover_service.verify_escalation_intent(runtime_transcript):
        return VoiceActionResponse(
            action=ActionType.TRANSFER_TO_MANAGER,
            spoken_text="I’ll help connect you with a team member.",
            word_count=8,
            play_hold_chime=True,
            department="human_escalation",
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )

    persona = (
        f"You are the {agent_pod_id} voice assistant. Be concise and courteous. "
        "Do not give medical diagnoses or claim an appointment or transfer has been completed."
    )
    try:
        spoken_text = await llm_service.generate_voice_response(persona, runtime_transcript)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Language model provider failed") from exc

    audio_url = await tts_service.fetch_pcm_stream_endpoint(spoken_text)
    return VoiceActionResponse(
        action=ActionType.SPEAK,
        spoken_text=spoken_text,
        word_count=len(spoken_text.split()),
        audio_url=audio_url,
        latency_ms=round((time.perf_counter() - started) * 1000, 2),
    )
