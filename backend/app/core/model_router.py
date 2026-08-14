from dataclasses import dataclass

@dataclass(frozen=True)
class RouteDecision:
    tier: str
    reason: str
    estimated_priority: str

def route(task: str, risk: str = "low", complexity: str = "simple") -> RouteDecision:
    risk, complexity = risk.lower(), complexity.lower()
    if risk in {"critical", "high"} or complexity in {"complex", "architecture"}:
        return RouteDecision("premium", "High-risk or complex reasoning requires escalation.", "high")
    if complexity in {"medium", "debug", "multifile"}:
        return RouteDecision("standard", "Multi-step engineering work needs a standard coding model.", "medium")
    return RouteDecision("fast", "Simple routine work should use the cheapest suitable tier.", "low")
