from app.services.planner import create_plan

def test_crm_plan_assembles_builder_and_verifier():
    plan = create_plan("Build a CRM with authentication, MongoDB and responsive UI")
    assert "Universal Builder" in plan["agents"]
    assert "QA/Test Engineer" in plan["agents"]
    assert "Security Engineer" in plan["agents"]
    assert "VERIFY" in plan["steps"]
    assert plan["approval_required"] is True
