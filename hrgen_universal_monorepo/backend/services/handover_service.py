import re


class HandoverService:
    def __init__(self) -> None:
        self.patterns = [
            r"\b(?:manager|human|supervisor|representative|real person)\b",
            r"\b(?:speak|talk|connect|transfer)\s+(?:to|with)\s+(?:a\s+)?(?:person|human|manager|supervisor)\b",
        ]

    def verify_escalation_intent(self, text: str) -> bool:
        normalized = text.casefold()
        return any(re.search(pattern, normalized) for pattern in self.patterns)


handover_service = HandoverService()
