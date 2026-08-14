from dataclasses import dataclass
@dataclass(frozen=True)
class BudgetDecision:
    tier:str; max_context_tokens:int; reason:str
def decide(task_type:str,complexity:str="simple",failure_count:int=0):
    if failure_count>=2 or complexity in {"critical","architectural"}:
        return BudgetDecision("premium",24000,"escalation_required")
    if complexity in {"normal","complex"}:
        return BudgetDecision("medium",12000,"standard_engineering")
    return BudgetDecision("fast",6000,"routine_or_deterministic")
