from dataclasses import dataclass, asdict
from threading import Lock
from uuid import uuid4
from datetime import datetime, timezone

@dataclass
class Node:
    id:str; task_id:str; name:str; agent_id:str; depends_on:list; state:str

class TaskGraph:
    def __init__(self):
        self._graphs={}; self._lock=Lock()
    def create(self,task_id,nodes):
        with self._lock:
            graph=[]
            for n in nodes:
                graph.append(Node(str(uuid4()),task_id,n["name"],n["agent_id"],n.get("depends_on",[]),"PENDING"))
            self._graphs[task_id]=graph
            return [asdict(x) for x in graph]
    def ready(self,task_id):
        with self._lock:
            g=self._graphs.get(task_id,[])
            done={n.id for n in g if n.state=="COMPLETED"}
            return [asdict(n) for n in g if n.state=="PENDING" and all(d in done for d in n.depends_on)]
    def transition(self,node_id,state):
        with self._lock:
            for g in self._graphs.values():
                for n in g:
                    if n.id==node_id:
                        n.state=state; return asdict(n)
            return None
    def get(self,task_id):
        with self._lock: return [asdict(n) for n in self._graphs.get(task_id,[])]

task_graph=TaskGraph()
