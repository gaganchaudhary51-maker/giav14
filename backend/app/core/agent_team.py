DOMAIN_AGENTS={
"ui":("ui_ux",["ui"]), "frontend":("frontend_engineer",["frontend"]),
"backend":("backend_engineer",["backend"]), "database":("database_engineer",["database"]),
"security":("security",["security"]), "qa":("qa",["qa"]), "devops":("devops",["devops"]),
"research":("research",["research"]), "analytics":("analytics",["analytics"]),
"rag":("rag_engineer",["rag"]), "ai":("ai_engineer",["ai"])
}
def assemble(task:str):
    t=task.lower();team=["project_manager"]
    if any(x in t for x in ["build","create","app","crm","saas","website"]):
        team+=["architect","ui_ux","frontend_engineer","backend_engineer","database_engineer","qa","security"]
    if any(x in t for x in ["voice","ai","agent","model","router"]):team+=["ai_engineer"]
    if any(x in t for x in ["memory","rag","document","knowledge"]):team+=["rag_engineer"]
    if any(x in t for x in ["deploy","release","rollback","docker"]):team+=["devops"]
    if any(x in t for x in ["research","analyze","market"]):team+=["research","analytics"]
    if any(x in t for x in ["fix","bug","error","broken"]):team+=["code_analyzer","debugger","qa","security"]
    return list(dict.fromkeys(team))
def skills_for_team(task):
    from app.skills.registry import skill_registry
    out={}
    for domain,(agent,_skills) in DOMAIN_AGENTS.items():
        if agent in assemble(task): out[agent]=[x["skill"] for x in skill_registry.for_domain(domain)]
    return out
