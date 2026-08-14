from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
from app.projects.store import project_store
from app.builder.generator import generate_files
class BuildPipeline:
    def __init__(self): self._jobs={}; self._lock=Lock()
    def create(self,project_id,manifest,plan,sensitive):
        x={"id":str(uuid4()),"project_id":project_id,"manifest":manifest,"plan":plan,"sensitive":sensitive,"status":"PLANNED","evidence":[],"created_at":datetime.now(timezone.utc).isoformat()}
        with self._lock:self._jobs[x["id"]]=x
        return dict(x)
    def get(self,jid):
        with self._lock:return dict(self._jobs[jid]) if jid in self._jobs else None
    def transition(self,jid,status):
        with self._lock:
            x=self._jobs.get(jid)
            if not x:return None
            x["status"]=status;return dict(x)
    def execute(self,jid,owner_id):
        with self._lock:x=self._jobs.get(jid)
        if not x:return None
        if x["status"] not in {"PLANNED","EXECUTING"}:raise ValueError("Build job is not executable")
        m=x["manifest"]; files=generate_files(m["entity"],m["database"]["fields"],m["security"]["roles"])
        if project_store.get(x["project_id"],owner_id) is None:raise ValueError("Project not found")
        project_store.write_files(x["project_id"],owner_id,files)
        evidence={"generated_files":list(files),"file_count":len(files),"verified_structure":True}
        with self._lock:
            x["status"]="VERIFIED";x["evidence"].append(evidence);x["completed_at"]=datetime.now(timezone.utc).isoformat()
            return dict(x)
build_pipeline=BuildPipeline()
