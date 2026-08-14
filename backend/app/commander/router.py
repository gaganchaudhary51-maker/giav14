from app.models.router import route_task
from app.agents.registry import agent_registry

def classify(text):
    t=text.lower()
    domains=[]
    if any(x in t for x in ["ui","design","screen","dashboard","mobile"]): domains.append("ui_ux")
    if any(x in t for x in ["build","code","app","bug","api","backend","frontend"]): domains.append("software_engineering")
    if any(x in t for x in ["database","mongodb","schema"]): domains.append("backend_database")
    if any(x in t for x in ["research","competitor","market","web"]): domains.append("research_intelligence")
    if any(x in t for x in ["test","security","deploy","release"]): domains.append("qa_security_devops")
    if any(x in t for x in ["voice","talk","speak","listen"]): domains.append("voice_conversation")
    if any(x in t for x in ["analytics","metric","kpi","data"]): domains.append("analytics")
    if not domains: domains=["software_engineering"]
    return sorted(set(domains))

def dispatch(text,risk="LOW",complexity="normal",failure_count=0):
    domains=classify(text)
    decision=route_task(text,risk,failure_count,complexity)
    agents=agent_registry.assemble(domains)
    return {"intent":text,"domains":domains,"model":decision.tier,
            "agents":agents,"requires_approval":risk.upper() in {"HIGH","CRITICAL"}}
