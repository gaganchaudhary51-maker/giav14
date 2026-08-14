from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
from threading import Lock

class AuditLog:
    def __init__(self):
        self.path=Path(os.getenv("GIA_AUDIT_LOG","/tmp/gia-audit/audit.jsonl"))
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self._lock=Lock()

    def _last_hash(self):
        if not self.path.exists(): return "GENESIS"
        lines=self.path.read_text(encoding="utf-8").splitlines()
        if not lines: return "GENESIS"
        return json.loads(lines[-1])["hash"]

    def append(self, event_type, actor, payload):
        with self._lock:
            record={
                "timestamp":datetime.now(timezone.utc).isoformat(),
                "event_type":event_type,
                "actor":actor,
                "payload":payload,
                "previous_hash":self._last_hash()
            }
            raw=json.dumps(record,sort_keys=True,separators=(",",":"))
            record["hash"]=hashlib.sha256(raw.encode()).hexdigest()
            with self.path.open("a",encoding="utf-8") as f:
                f.write(json.dumps(record,sort_keys=True)+"\n")
            return record

audit_log=AuditLog()
