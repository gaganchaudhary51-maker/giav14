from backend.services.handover_service import HandoverService
from backend.schemas.voice import ActionType, VoiceActionResponse


def test_handover_detects_explicit_human_request():
    service = HandoverService()
    assert service.verify_escalation_intent("Please connect me to a human")
    assert service.verify_escalation_intent("I want to speak to a manager")


def test_handover_does_not_escalate_unrelated_sentence():
    service = HandoverService()
    assert not service.verify_escalation_intent("Can you tell me your opening hours?")


def test_voice_response_schema():
    result = VoiceActionResponse(
        action=ActionType.SPEAK,
        spoken_text="How can I help?",
        word_count=4,
    )
    assert result.word_count == 4
    assert result.audio_url is None
