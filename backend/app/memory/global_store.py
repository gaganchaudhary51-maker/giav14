from pathlib import Path
import json, re

class GlobalKnowledge:
    def __init__(self):
        p=Path(__file__).resolve().parents[3] / "knowledge" / "GLOBAL-MEMORY-SEED.json"
        self.data=json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
        self.documents=[]
        for project in self.data.get("projects",[]):
            for text in project.get("knowledge",[]):
                self.documents.append({"scope":"global","project_id":project["id"],"project":project["name"],"text":text})
        for skill in self.data.get("global_agent_skills",[]):
            self.documents.append({"scope":"global-skill","skill":skill["skill"],"text":skill["description"]})
        for decision in self.data.get("global_decisions",[]):
            self.documents.append({"scope":"global-decision","text":decision})

    def search(self, query, limit=10):
        terms=[t for t in re.findall(r"[a-z0-9_+-]+",query.lower()) if len(t)>1]
        scored=[]
        for doc in self.documents:
            text=json.dumps(doc,ensure_ascii=False).lower()
            score=sum(text.count(t) for t in terms)
            if score:
                scored.append((score,doc))
        scored.sort(key=lambda x:-x[0])
        return [d for _,d in scored[:max(1,min(limit,20))]]

global_knowledge=GlobalKnowledge()
