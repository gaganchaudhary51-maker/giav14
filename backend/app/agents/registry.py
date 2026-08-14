from dataclasses import dataclass, asdict
from typing import List

@dataclass(frozen=True)
class AgentProfile:
    id:str
    role:str
    domains:List[str]
    capabilities:List[str]

AGENTS=[
 AgentProfile("planner","Project Planner",["planning","requirements"],["specification","task_graph","risk"]),
 AgentProfile("architect","Software Architect",["software_engineering","app_builder"],["architecture","decomposition","tradeoffs"]),
 AgentProfile("ui","UI/UX Agent",["ui_ux"],["design_system","responsive_ui","accessibility"]),
 AgentProfile("frontend","Frontend Engineer",["software_engineering","ui_ux"],["react","typescript","testing"]),
 AgentProfile("backend","Backend Engineer",["software_engineering","backend_database"],["fastapi","api","validation"]),
 AgentProfile("database","Database Engineer",["backend_database"],["mongodb","schema","migration"]),
 AgentProfile("research","Research Agent",["research_intelligence"],["web_research","synthesis"]),
 AgentProfile("qa","QA Agent",["qa_security_devops"],["tests","regression","verification"]),
 AgentProfile("security","Security Agent",["qa_security_devops"],["threat_model","secrets","permissions"]),
 AgentProfile("devops","DevOps Agent",["qa_security_devops"],["build","release","rollback"]),
 AgentProfile("analytics","Analytics Agent",["analytics"],["metrics","diagnostics","reporting"]),
 AgentProfile("voice","Voice Agent",["voice_conversation"],["stt","tts","conversation"])
]

class AgentRegistry:
    def list(self): return [asdict(a) for a in AGENTS]
    def get(self,agent_id):
        for a in AGENTS:
            if a.id==agent_id: return asdict(a)
        return None
    def assemble(self,domains,capabilities=None):
        capabilities=set(capabilities or [])
        selected=[]
        for a in AGENTS:
            domain_hit=bool(set(a.domains)&set(domains))
            capability_hit=bool(capabilities & set(a.capabilities))
            if domain_hit or capability_hit: selected.append(asdict(a))
        return selected

agent_registry=AgentRegistry()
