from fastapi import APIRouter,Header,HTTPException
from pydantic import BaseModel,Field
from app.auth.security import verify_token
from app.orchestration.graph import task_graph
from app.agents.registry import agent_registry
from app.orchestration.runner import runner
from app.audit.log import audit_log
router=APIRouter(prefix="/orchestration",tags=["orchestration"])
class Node(BaseModel):
    name:str=Field(min_length=1,max_length=100);agent_id:str=Field(min_length=1,max_length=100);depends_on:list[str]=Field(default_factory=list,max_length=20)
class Graph(BaseModel): task_id:str=Field(min_length=1,max_length=200);nodes:list[Node]=Field(min_length=1,max_length=50)
class Start(BaseModel): task_id:str
class Complete(BaseModel): task_id:str;evidence:list[dict]=Field(default_factory=list)
class Fail(BaseModel): task_id:str;risk:str="LOW"
def auth(a):
    if not a or not a.startswith("Bearer "):raise HTTPException(401,"Authentication required")
    uid=verify_token(a[7:])
    if not uid:raise HTTPException(401,"Invalid or expired token")
    return uid
@router.post("/graph")
def create(payload:Graph,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    for n in payload.nodes:
        if not agent_registry.get(n.agent_id):raise HTTPException(400,f"Unknown agent: {n.agent_id}")
    out=task_graph.create(payload.task_id,[n.model_dump() for n in payload.nodes]);audit_log.append("TASK_GRAPH_CREATED",uid,{"task_id":payload.task_id,"nodes":out})
    return {"task_id":payload.task_id,"nodes":out}
@router.get("/graph/{task_id}")
def get(task_id:str,authorization:str|None=Header(default=None)):
    auth(authorization);return {"nodes":task_graph.get(task_id),"ready":task_graph.ready(task_id)}
@router.post("/node/{node_id}/{state}")
def transition(node_id:str,state:str,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    if state not in {"RUNNING","COMPLETED","FAILED","BLOCKED"}:raise HTTPException(400,"Invalid node state")
    out=task_graph.transition(node_id,state)
    if not out:raise HTTPException(404,"Node not found")
    audit_log.append("AGENT_NODE_TRANSITION",uid,out);return out
@router.post("/start")
def start(payload:Start,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    try:out=runner.start(payload.task_id)
    except KeyError as e:raise HTTPException(404,str(e))
    audit_log.append("ORCHESTRATION_STARTED",uid,out);return out
@router.post("/complete")
def complete(payload:Complete,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    try:out=runner.complete(payload.task_id,bool(payload.evidence),payload.evidence)
    except KeyError as e:raise HTTPException(404,str(e))
    audit_log.append("ORCHESTRATION_COMPLETED",uid,out);return out
@router.post("/fail")
def fail(payload:Fail,authorization:str|None=Header(default=None)):
    uid=auth(authorization)
    try:out=runner.fail_and_escalate(payload.task_id,payload.risk)
    except KeyError as e:raise HTTPException(404,str(e))
    audit_log.append("ORCHESTRATION_ESCALATED",uid,out);return out
