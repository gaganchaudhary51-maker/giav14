from dataclasses import dataclass, field
from typing import Any

@dataclass
class AppSpec:
    name: str
    frontend: str = "react-typescript"
    backend: str = "fastapi"
    database: str = "mongodb"
    authentication: bool = True
    roles: list[str] = field(default_factory=lambda: ["admin", "user"])
    resources: list[str] = field(default_factory=list)

    def normalized(self) -> dict[str, Any]:
        return {
            "name": self.name.strip(),
            "frontend": self.frontend,
            "backend": self.backend,
            "database": self.database,
            "authentication": self.authentication,
            "roles": list(dict.fromkeys(self.roles)),
            "resources": list(dict.fromkeys(r.strip().lower() for r in self.resources if r.strip())),
        }
