from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CallChannel(str, Enum):
    VOICE_WEBPHONE = "VOICE_WEBPHONE"
    VOIP_SIP_TRUNK = "VOIP_SIP_TRUNK"
    WHATSAPP_VOICE = "WHATSAPP_VOICE"


class ActionType(str, Enum):
    SPEAK = "SPEAK"
    TRANSFER_TO_MANAGER = "TRANSFER_TO_MANAGER"
    HOLD = "HOLD"
    HANGUP = "HANGUP"


class VoiceActionResponse(BaseModel):
    action: ActionType
    spoken_text: str
    word_count: int
    audio_url: str | None = None
    play_hold_chime: bool = False
    sip_transfer_uri: str | None = None
    department: str | None = None
    latency_ms: float | None = None


class TranscriptInput(BaseModel):
    call_id: str = Field(min_length=1, max_length=128)
    caller_id: str = Field(min_length=1, max_length=128)
    agent_pod_id: str = Field(min_length=1, max_length=80)
    channel: CallChannel = CallChannel.VOIP_SIP_TRUNK
    transcript: str = Field(default="", max_length=12000)
    session_metadata: dict[str, Any] | None = None
