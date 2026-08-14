from dataclasses import dataclass

@dataclass(frozen=True)
class ContextPack:
    summary:str
    selected_files:list[str]
    selected_memory:list[str]
    estimated_chars:int

def build_context(task:str, files:list[str], memories:list[str], char_budget:int=12000) -> ContextPack:
    selected=[]
    used=0
    for item in files:
        cost=len(item)
        if used+cost<=char_budget//2:
            selected.append(item); used+=cost
    mem=[]
    for item in memories:
        cost=len(item)
        if used+cost<=char_budget:
            mem.append(item); used+=cost
    summary=f"Task: {task[:500]} | selected_files={len(selected)} | selected_memory={len(mem)}"
    return ContextPack(summary,selected,mem,used+len(summary))
