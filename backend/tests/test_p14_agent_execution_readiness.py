"""P14 regression checks: registry consistency is not mistaken for live agent execution."""
from app.agents.registry import AGENTS, LEGACY_AGENT_IDS, agent_registry
from app.core.agent_team import assemble as legacy_assemble
from app.services.agent_router import assemble_team, canonical_team
from app.execution.runner import ALLOWED_ACTIONS, BLOCKED_ACTIONS


EXPECTED_IDS = {
    "planner", "architect", "ui", "frontend", "backend", "database",
    "research", "qa", "security", "devops", "analytics", "voice",
}


def test_public_registry_has_twelve_unique_canonical_agents():
    ids = [agent.id for agent in AGENTS]
    assert set(ids) == EXPECTED_IDS
    assert len(ids) == len(set(ids)) == 12
    assert all(agent_registry.get(agent_id) for agent_id in ids)


def test_legacy_aliases_resolve_only_to_registered_canonical_ids():
    ids = set(agent.id for agent in AGENTS)
    assert LEGACY_AGENT_IDS
    assert all(target in ids for target in LEGACY_AGENT_IDS.values())
    assert all(agent_registry.canonical_id(alias) == target
               for alias, target in LEGACY_AGENT_IDS.items())


def test_keyword_router_canonical_ids_are_registered():
    samples = [
        "build a responsive website",
        "debug a FastAPI endpoint",
        "review database security and deploy",
        "research market analytics",
        "voice conversation agent",
    ]
    ids = set(agent.id for agent in AGENTS)
    for task in samples:
        assert set(canonical_team(task)) <= ids
        assert assemble_team(task)  # legacy display-name router remains active


def test_legacy_domain_router_labels_normalize_without_rewriting_old_chat_or_memory():
    ids = set(agent.id for agent in AGENTS)
    for task in ["build app", "fix bug", "memory RAG document", "voice agent", "deploy release"]:
        labels = legacy_assemble(task)
        normalized = agent_registry.resolve_names(labels)
        assert set(normalized) <= ids
        assert labels  # legacy route still returns its established labels


def test_execution_actions_are_allowlisted_and_sensitive_actions_are_blocked():
    assert {"READ_FILE", "LIST_FILES", "RUN_TESTS", "RUN_BUILD", "LINT", "FORMAT"} <= ALLOWED_ACTIONS
    assert {"DELETE", "DROP_DATABASE", "SECRET_READ", "PRODUCTION_DEPLOY", "UNRESTRICTED_SHELL"} <= BLOCKED_ACTIONS
