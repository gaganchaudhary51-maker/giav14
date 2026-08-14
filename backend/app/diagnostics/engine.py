from dataclasses import dataclass, asdict
from datetime import datetime, timezone

@dataclass
class Diagnostic:
    component:str; severity:str; message:str; evidence:str; created_at:str

def diagnose(component,exc=None,evidence=""):
    return asdict(Diagnostic(component,"ERROR" if exc else "INFO",
        str(exc) if exc else "No exception; inspect supplied evidence.",evidence,
        datetime.now(timezone.utc).isoformat()))

def repair_plan(diagnostic):
    return {"status":"PROPOSED","component":diagnostic["component"],
        "steps":["isolate affected component","inspect relevant evidence",
                 "propose minimal change","run targeted tests",
                 "run regression tests","checkpoint only after verification"]}
