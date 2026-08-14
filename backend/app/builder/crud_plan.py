from .spec import AppSpec

def build_crud_plan(spec: AppSpec) -> dict:
    s = spec.normalized()
    files = [
        "frontend/src/app.tsx",
        "frontend/src/auth/",
        "frontend/src/components/",
        "frontend/src/pages/dashboard.tsx",
        "backend/app/main.py",
        "backend/app/routes/",
        "backend/app/models/",
        "backend/app/services/",
        "backend/tests/",
        "README.md",
        ".env.example",
    ]
    collections = [f"{r}s" if not r.endswith("s") else r for r in s["resources"]]
    return {
        "project": s["name"],
        "stack": {"frontend": s["frontend"], "backend": s["backend"], "database": s["database"]},
        "auth": {"enabled": s["authentication"], "roles": s["roles"]},
        "resources": s["resources"],
        "mongodb_collections": collections,
        "planned_files": files,
        "operations": ["create", "read", "update", "delete", "search", "validate"],
        "verification": ["frontend_build", "backend_tests", "api_tests", "crud_tests", "responsive_check"],
    }
