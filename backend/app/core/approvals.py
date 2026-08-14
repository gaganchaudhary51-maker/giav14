HIGH_RISK = {
    "delete_files", "destructive_db_change", "production_data_change",
    "secret_access", "external_account_change", "production_deploy"
}

def requires_approval(action: str) -> bool:
    return action in HIGH_RISK

def approval_summary(action: str, target: str, reason: str) -> dict:
    return {
        "required": requires_approval(action),
        "action": action,
        "target": target,
        "reason": reason,
        "rollback": "checkpoint-before-action",
    }
