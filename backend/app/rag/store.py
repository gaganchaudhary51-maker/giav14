from dataclasses import dataclass,asdict
from datetime import datetime,timezone
from threading import Lock
from uuid import uuid4
import re,math
@dataclass
class Chunk:
    id:str; user_id:str; project_id:str; source:str; text:str; terms:list[str]; created_at:str
class RAGStore:
    def __init__(self): self._items={}; self._lock=Lock()
    def _terms(self,text):
        return [x for x in re.findall(r"[a-zA-Z0-9_]{2,}",text.lower()) if x not in {"the","and","for","with","this","that"}]
    def index(self,user_id,project_id,source,text,chunk_size=1800,overlap=200):
        if not text.strip(): return []
        words=text.split(); step=max(1,chunk_size-overlap); out=[]
        with self._lock:
            for i in range(0,len(words),step):
                chunk_text=" ".join(words[i:i+chunk_size]).strip()
                if not chunk_text: continue
                c=Chunk(str(uuid4()),user_id,project_id,source,chunk_text,self._terms(chunk_text),datetime.now(timezone.utc).isoformat())
                self._items[c.id]=c; out.append(asdict(c))
                if i+chunk_size>=len(words): break
        return out
    def search(self,user_id,project_id,query,limit=5):
        q=self._terms(query)
        if not q:return []
        with self._lock: items=[c for c in self._items.values() if c.user_id==user_id and c.project_id==project_id]
        scored=[]
        for c in items:
            counts={t:c.terms.count(t) for t in set(c.terms)}
            score=sum(1+math.log1p(counts.get(t,0)) for t in q if counts.get(t,0))
            if score:scored.append((score,c))
        scored.sort(key=lambda x:(-x[0],x[1].created_at))
        return [asdict(c) for _,c in scored[:limit]]
    def clear_project(self,user_id,project_id):
        with self._lock:
            ids=[k for k,v in self._items.items() if v.user_id==user_id and v.project_id==project_id]
            for k in ids:del self._items[k]
            return len(ids)
rag_store=RAGStore()
