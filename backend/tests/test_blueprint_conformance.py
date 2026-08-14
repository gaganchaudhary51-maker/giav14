from pathlib import Path
import json,hashlib

ROOT=Path(__file__).resolve().parents[2]
GOV=ROOT/"GOVERNANCE"

def test_blueprint_is_locked_and_unchanged():
    p=GOV/"BLUEPRINT-PATH.json"
    assert p.exists()
    m=json.loads((GOV/"BLUEPRINT-CONFORMANCE-MATRIX.json").read_text())
    assert m["blueprint_status"]=="LOCKED"
    assert m["blueprint_sha256"]==hashlib.sha256(p.read_bytes()).hexdigest()

def test_required_architecture_paths_present():
    m=json.loads((GOV/"BLUEPRINT-CONFORMANCE-MATRIX.json").read_text())
    assert not m["missing_paths"], m["missing_paths"]
