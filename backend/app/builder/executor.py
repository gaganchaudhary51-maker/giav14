from pathlib import Path
import json
from datetime import datetime, timezone

def materialize_plan(plan: dict, workspace: str) -> dict:
    root = Path(workspace).resolve()
    root.mkdir(parents=True, exist_ok=True)
    checkpoint = root / ".gia-checkpoints"
    checkpoint.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    manifest = checkpoint / f"{stamp}.json"
    manifest.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return {"status":"checkpointed","workspace":str(root),
            "checkpoint":str(manifest),"files_planned":len(plan.get("planned_files",[]))}
