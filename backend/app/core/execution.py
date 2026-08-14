from dataclasses import dataclass
from enum import Enum

class ExecutionState(str, Enum):
    REQUESTED="REQUESTED"; PLANNED="PLANNED"; APPROVAL_REQUIRED="APPROVAL_REQUIRED"
    APPROVED="APPROVED"; EXECUTING="EXECUTING"; EXECUTED="EXECUTED"
    VERIFYING="VERIFYING"; VERIFIED="VERIFIED"; RELEASED="RELEASED"
    FAILED="FAILED"; DIAGNOSING="DIAGNOSING"; REPAIRING="REPAIRING"
    RETESTING="RETESTING"; ROLLED_BACK="ROLLED_BACK"

@dataclass
class Evidence:
    state: ExecutionState
    message: str
    checks: list[str]

def verified(evidence: Evidence) -> bool:
    return evidence.state == ExecutionState.VERIFIED and bool(evidence.checks)
