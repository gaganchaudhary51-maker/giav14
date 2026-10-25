from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from app.auth.security import verify_token
from app.agents.registry import agent_registry

router=APIRouter(prefix="/agents",tags=["agents"])
class Assemble(BaseModel):
    domains:list[str]=Field(default_factory=list,max_length=20)
    capabilities:list[str]=Field(default_factory=list,max_length=50)
def auth(a):
    if not a or not a.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    uid = verify_token(a[7:])
    if not uid:
        raise HTTPException(401, "Authentication required")
    return uid
@router.get("")
def list_agents(authorization:str|None=Header(default=None)):
    auth(authorization); return {"agents":agent_registry.list()}
@router.post("/assemble")
def assemble(payload:Assemble,authorization:str|None=Header(default=None)):
    auth(authorization); return {"agents":agent_registry.assemble(payload.domains,payload.capabilities)}

@router.get("/aliases")
def aliases(authorization:str|None=Header(default=None)):
    """List legacy labels mapped to canonical public agent IDs."""
    auth(authorization)
    return {"canonical_ids": [a["id"] for a in agent_registry.list()],
            "aliases": agent_registry.aliases()}

class ResolveNames(BaseModel):
    names:list[str]=Field(default_factory=list,max_length=100)

@router.post("/resolve")
def resolve_names(payload:ResolveNames,authorization:str|None=Header(default=None)):
    auth(authorization)
    unresolved = [name for name in payload.names if agent_registry.canonical_id(name) is None]
    return {"agents": agent_registry.resolve_names(payload.names),
            "unresolved": unresolved}


@router.get("/runtime")
def runtime_status(authorization:str|None=Header(default=None)):
    auth(authorization)
    from app.agents.provider_adapter import runtime_status as get_runtime_status
    return get_runtime_status()


class AgentInvoke(BaseModel):
    task_id: str = Field(min_length=1, max_length=200)
    prompt: str = Field(min_length=1, max_length=12000)


@router.post("/{agent_id}/invoke")
def invoke_agent(agent_id: str, payload: AgentInvoke,
                 authorization:str|None=Header(default=None)):
    """Explicit model-only call. Requires task ownership and EXECUTING state; no memory/tools attached."""
    uid = auth(authorization)
    from app.tasks.store import task_store
    task = task_store.get(payload.task_id)
    if not task or task.get("owner_id") != uid:
        raise HTTPException(404, "Task not found")
    if task.get("status") != "EXECUTING":
        raise HTTPException(409, "Task must be in EXECUTING state before agent invocation")
    from app.agents.provider_adapter import invoke as provider_invoke
    try:
        result = provider_invoke(agent_id, payload.prompt)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    except RuntimeError as exc:
        reason = str(exc)
        status = 503 if reason.startswith("provider_") or reason in {
            "base_url_must_use_https_or_loopback", "invalid_base_url"
        } else 503
        raise HTTPException(status, {"error": "Agent provider unavailable", "reason": reason}) from None
    from app.audit.log import audit_log
    audit_log.append("AGENT_MODEL_INVOKED", uid, {
        "task_id": payload.task_id, "agent_id": result["agent_id"],
        "provider": result["provider"], "model": result["model"],
        "status": result["status"], "personal_memory_attached": False,
        "tools_invoked": []
    })
    return result


class AgentRunRequest(BaseModel):
    """Run a small, explicit team against an already-authorized task."""
    task_id: str = Field(min_length=1, max_length=200)
    agent_ids: list[str] = Field(min_length=1, max_length=5)
    prompt: str = Field(min_length=1, max_length=12000)


@router.post("/run")
def run_agent_team(payload: AgentRunRequest,
                   authorization: str | None = Header(default=None)):
    """Execute up to five model-only agent calls in sequence.

    Calls are opt-in through provider configuration. The endpoint does not attach
    personal RAG/memory or enable tool execution. Each agent result/failure is
    returned and audit-logged independently.
    """
    uid = auth(authorization)
    from app.tasks.store import task_store
    task = task_store.get(payload.task_id)
    if not task or task.get("owner_id") != uid:
        raise HTTPException(404, "Task not found")
    if task.get("status") != "EXECUTING":
        raise HTTPException(409, "Task must be in EXECUTING state before agent execution")

    from app.agents.registry import agent_registry
    canonical_ids = []
    unresolved = []
    for requested in payload.agent_ids:
        canonical = agent_registry.canonical_id(requested)
        if canonical is None:
            unresolved.append(requested)
        elif canonical not in canonical_ids:
            canonical_ids.append(canonical)
    if unresolved:
        raise HTTPException(400, {"error": "Unknown agent ID", "unresolved": unresolved})
    if not canonical_ids:
        raise HTTPException(400, "At least one unique agent ID is required")

    from app.agents.provider_adapter import invoke as provider_invoke
    from app.audit.log import audit_log
    results = []
    for agent_id in canonical_ids:
        try:
            result = provider_invoke(agent_id, payload.prompt)
            results.append({"agent_id": agent_id, "status": "COMPLETED",
                            "output": result["output"], "provider": result["provider"],
                            "model": result["model"], "personal_memory_attached": False,
                            "tools_invoked": []})
            audit_log.append("AGENT_TEAM_MEMBER_COMPLETED", uid, {
                "task_id": payload.task_id, "agent_id": agent_id,
                "status": "COMPLETED", "personal_memory_attached": False,
                "tools_invoked": []
            })
        except (ValueError, RuntimeError) as exc:
            reason = str(exc) if isinstance(exc, RuntimeError) else "invalid_agent_request"
            results.append({"agent_id": agent_id, "status": "FAILED", "error": reason,
                            "personal_memory_attached": False, "tools_invoked": []})
            audit_log.append("AGENT_TEAM_MEMBER_FAILED", uid, {
                "task_id": payload.task_id, "agent_id": agent_id,
                "status": "FAILED", "reason": reason,
                "personal_memory_attached": False, "tools_invoked": []
            })
    completed = sum(item["status"] == "COMPLETED" for item in results)
    status = "COMPLETED" if completed == len(results) else ("FAILED" if completed == 0 else "PARTIAL")
    return {"task_id": payload.task_id, "status": status, "requested_count": len(canonical_ids),
            "completed_count": completed, "results": results,
            "personal_memory_attached": False, "tool_execution_enabled": False}
