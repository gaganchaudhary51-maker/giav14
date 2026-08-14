from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.projects import router as projects_router
from app.routes.tasks import router as tasks_router
app=FastAPI(title='GIA Universal AI API',version='0.1.0')
app.include_router(health_router,prefix='/api')
app.include_router(projects_router,prefix='/api')
@app.get('/api')
def root(): return {'service':'gia-universal-ai','status':'ok'}


from pydantic import BaseModel
from app.core.model_router import route
from app.core.approvals import approval_summary

class RouteRequest(BaseModel):
    task: str
    risk: str = "low"
    complexity: str = "simple"

@app.post("/api/governance/route")
def governance_route(payload: RouteRequest):
    return route(payload.task, payload.risk, payload.complexity).__dict__

class ApprovalRequest(BaseModel):
    action: str
    target: str
    reason: str

@app.post("/api/governance/approval")
def governance_approval(payload: ApprovalRequest):
    return approval_summary(payload.action, payload.target, payload.reason)

from app.routes.builder import router as builder_router
app.include_router(builder_router, prefix='/api')

@app.get("/api/system/persistence")
def persistence_status():
    from app.repositories.project_repository import store
    return {"backend": "mongodb" if store._collection is not None else "memory-fallback",
            "production_ready": store._collection is not None}

from app.routes.auth import router as auth_router
from app.routes.conversation import router as conversation_router
app.include_router(auth_router, prefix='/api')
app.include_router(conversation_router, prefix='/api')

from app.routes.sandbox import router as sandbox_router
app.include_router(sandbox_router, prefix='/api')

from app.routes.events import router as events_router
app.include_router(tasks_router,prefix='/api')
app.include_router(events_router,prefix='/api')

from app.routes.audit import router as audit_router
app.include_router(audit_router,prefix='/api')

from app.routes.memory import router as memory_router
app.include_router(memory_router,prefix='/api')

from app.routes.global_memory import router as global_memory_router
app.include_router(global_memory_router,prefix='/api')

from app.routes.skills import router as skills_router
app.include_router(skills_router,prefix='/api')

from app.routes.learning import router as learning_router
app.include_router(learning_router,prefix='/api')

from app.routes.collaboration import router as collaboration_router
app.include_router(collaboration_router,prefix='/api')

from app.routes.approvals import router as approvals_router
app.include_router(approvals_router,prefix='/api')

from app.routes.verification import router as verification_router
app.include_router(verification_router,prefix='/api')

from app.routes.models import router as models_router
app.include_router(models_router,prefix='/api')

from app.routes.checkpoints import router as checkpoints_router
app.include_router(checkpoints_router,prefix='/api')

from app.routes.execution import router as execution_router
app.include_router(execution_router,prefix='/api')

from app.routes.agents import router as agents_router
app.include_router(agents_router,prefix='/api')

from app.routes.orchestration import router as orchestration_router
app.include_router(orchestration_router,prefix='/api')

from app.routes.commander import router as commander_router
app.include_router(commander_router,prefix='/api')

from app.routes.workspace import router as workspace_router
app.include_router(workspace_router,prefix='/api')

from app.routes.rag import router as rag_router
app.include_router(rag_router,prefix='/api')

from app.routes.voice import router as voice_router
app.include_router(voice_router,prefix='/api')
