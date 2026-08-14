from dataclasses import dataclass

@dataclass(frozen=True)
class AgentRoute:
    name: str
    reason: str
    priority: int

KEYWORDS = {
    "ui": ["ui", "ux", "screen", "design", "responsive", "mobile"],
    "frontend": ["frontend", "react", "component", "page", "form"],
    "backend": ["backend", "api", "fastapi", "endpoint", "server"],
    "database": ["database", "mongodb", "mongo", "schema", "collection", "migration"],
    "security": ["security", "permission", "role", "auth", "secret", "login"],
    "qa": ["test", "bug", "error", "qa", "verify", "regression"],
    "research": ["research", "analyze", "competitor", "market", "document"],
    "builder": ["build", "create", "generate", "app", "application", "crm", "erp", "saas"],
    "devops": ["deploy", "deployment", "docker", "release", "production"],
}

AGENT_NAMES = {
    "ui": "UI/UX",
    "frontend": "Frontend Engineer",
    "backend": "Backend Engineer",
    "database": "Database Engineer",
    "security": "Security Engineer",
    "qa": "QA/Test Engineer",
    "research": "Research Engineer",
    "builder": "Universal Builder",
    "devops": "DevOps Engineer",
}

def assemble_team(request: str) -> list[AgentRoute]:
    text = request.lower()
    selected: list[AgentRoute] = []
    for key, words in KEYWORDS.items():
        if any(w in text for w in words):
            selected.append(AgentRoute(AGENT_NAMES[key], f"Matched task signals for {key}", 10))
    if not selected:
        selected = [AgentRoute("Project Manager", "Default orchestration for ambiguous requests", 10)]
    # Every build/change needs verification; security is mandatory for auth/data/deploy signals.
    names = {a.name for a in selected}
    if any(x in text for x in ["build", "create", "generate", "fix", "change"]):
        if "QA/Test Engineer" not in names:
            selected.append(AgentRoute("QA/Test Engineer", "Required verification gate", 20))
    if any(x in text for x in ["auth", "login", "role", "permission", "secret", "deploy", "production", "database"]):
        if "Security Engineer" not in names:
            selected.append(AgentRoute("Security Engineer", "Required security review for sensitive scope", 20))
    return selected
