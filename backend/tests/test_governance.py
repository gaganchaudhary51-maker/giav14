from app.core.model_router import route
from app.core.approvals import requires_approval
from app.core.execution import ExecutionState, Evidence, verified
from app.core.agent_team import assemble

def test_fast_routing():
    assert route("format text").tier == "fast"

def test_premium_routing():
    assert route("production migration", risk="critical").tier == "premium"

def test_approval_gate():
    assert requires_approval("production_deploy")
    assert not requires_approval("run_tests")

def test_evidence_gate():
    assert not verified(Evidence(ExecutionState.EXECUTED, "generated", []))
    assert verified(Evidence(ExecutionState.VERIFIED, "tests passed", ["unit-test-1"]))

def test_dynamic_team():
    team = assemble("build customer CRM")
    assert "backend_engineer" in team
    assert "qa" in team
    assert "security" in team
