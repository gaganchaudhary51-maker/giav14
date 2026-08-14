from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

@dataclass
class Task:
    id: str
    project_id: str
    request: str
    status: str = "REQUESTED"
    plan: list[str] = field(default_factory=list)
    agents: list[str] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=now_iso)
    updated_at: str = field(default_factory=now_iso)
