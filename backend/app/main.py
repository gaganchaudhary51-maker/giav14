from pathlib import Path
from dotenv import load_dotenv

# Load the documented local configuration before stores and providers initialize.
# Explicit process settings (including the desktop sidecar) take precedence.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

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
    from app.db.sqlite import database_path
    from app.db.user_store import user_store
    return {
        "backend": "mongodb" if store._collection is not None else "sqlite",
        "project_store": "mongodb" if store._collection is not None else "sqlite",
        "user_store": "mongodb" if user_store._collection is not None else "sqlite",
        "task_store": "sqlite",
        "approval_store": "sqlite",
        "execution_store": "sqlite",
        "rag_store": "sqlite",
        "memory_store": "sqlite",
        "database_path": str(database_path()),
        "production_ready": False,
        "notes": [
            "Projects, users, tasks, approvals, execution records, RAG chunks, and project memories persist locally in SQLite when MongoDB is not configured.",
            "MongoDB remains supported for projects and users when configured and reachable.",
            "Task and execution lifecycle operations require authenticated ownership; execution actions remain allowlisted.",
            "Production readiness still requires backup/restore drills, deployment secrets, frontend production build, and end-to-end verification."
        ]
    }

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

from app.routes.studio import router as studio_router
app.include_router(studio_router, prefix="/api")
# Compatibility aliases matching the requested API contract.
from app.routes.studio import propose_evolution as _studio_propose_evolution
from app.routes.studio import review_evolution as _studio_review_evolution
from app.routes.studio import pending_evolutions as _studio_pending_evolutions
app.add_api_route("/api/agent/evolve", _studio_propose_evolution, methods=["POST"], tags=["studio"])
app.add_api_route("/api/agent/evolve/{proposal_id}/review", _studio_review_evolution, methods=["POST"], tags=["studio"])
app.add_api_route("/api/agent/evolve/pending", _studio_pending_evolutions, methods=["GET"], tags=["studio"])

from app.routes.telephony import router as telephony_router
app.include_router(telephony_router, prefix="/api")

# The installed Windows desktop app serves its bundled React build from the same
# loopback origin as the API. The normal browser/dev-server workflow remains unchanged.
import os
from app.desktop.static import mount_desktop_frontend
mount_desktop_frontend(app, os.getenv("GIA_FRONTEND_DIST", ""))
