from app.rag.store import rag_store
from app.memory.store import memory_store
def retrieve(user_id,project_id,query,limit=5):
    return {"documents":rag_store.search(user_id,project_id,query,limit),
            "memories":memory_store.search(user_id,project_id,query,limit)}
