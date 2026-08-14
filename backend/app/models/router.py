from dataclasses import dataclass

@dataclass(frozen=True)
class RouteDecision:
    tier:str
    reason:str
    max_context_chars:int
    max_retries:int

def route_task(text:str, risk:str="LOW", failure_count:int=0, complexity:str="normal") -> RouteDecision:
    t=text.lower()
    if risk.upper() in {"HIGH","CRITICAL"} or failure_count>=2 or complexity.lower()=="hard":
        return RouteDecision("premium","high risk/complexity or repeated failure",24000,1)
    if any(k in t for k in ["build","debug","refactor","api","database","migration"]):
        return RouteDecision("medium","engineering task",14000,2)
    return RouteDecision("fast","routine task",7000,2)

def escalate(current:RouteDecision,failure_count:int,risk:str="LOW") -> RouteDecision:
    if risk.upper() in {"HIGH","CRITICAL"} or failure_count>=2:
        return RouteDecision("premium","escalated after risk/failure threshold",24000,1)
    if current.tier=="fast":
        return RouteDecision("medium","fast tier failed; escalating",14000,2)
    return current
