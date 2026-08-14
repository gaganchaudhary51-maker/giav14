from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from uuid import uuid4
from app.auth.security import verify_token
from app.core.agent_team import assemble
from app.core.model_router import route
from app.core.approvals import requires_approval

router = APIRouter(prefix="/conversation", tags=["conversation"])

class Message(BaseModel):
    project_id: str | None = None
    text: str = Field(min_length=1, max_length=10000)

@router.post("/plan")
def plan(payload: Message, authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer ") or not verify_token(authorization[7:]):
        raise HTTPException(401, "Authentication required")
    team = assemble(payload.text)
    decision = route(payload.text)
    approval = requires_approval("production_deploy") if any(x in payload.text.lower() for x in ["deploy", "production"]) else False
    task_id = str(uuid4())
    return {
        "task_id": task_id,
        "status": "planned",
        "intent": payload.text,
        "team": team,
        "model_tier": decision.tier,
        "reason": decision.reason,
        "approval_required": approval,
        "next": "approval" if approval else "execution"
    }
