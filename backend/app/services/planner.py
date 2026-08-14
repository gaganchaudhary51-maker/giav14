from .agent_router import assemble_team

def create_plan(request: str) -> dict:
    team = assemble_team(request)
    lower = request.lower()
    steps = ["UNDERSTAND", "PLAN"]
    if any(x in lower for x in ["build", "create", "generate", "app", "saas", "crm", "erp"]):
        steps += ["ARCHITECT", "IMPLEMENT", "BUILD", "TEST", "VERIFY"]
    elif any(x in lower for x in ["fix", "bug", "error"]):
        steps += ["DIAGNOSE", "PATCH", "BUILD", "TEST", "REGRESSION", "VERIFY"]
    else:
        steps += ["EXECUTE", "VERIFY"]
    return {"steps": steps, "agents": [a.name for a in team], "approval_required": any(a.name in {"Security Engineer", "DevOps Engineer"} for a in team)}
