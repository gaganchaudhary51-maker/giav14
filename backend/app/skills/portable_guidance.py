"""Portable agent procedures loaded directly into GIA agent system prompts."""

_SKILLS = {
    "systematic-debugging": (
        "For bugs, establish the observed failure and evidence first; trace to a root cause before proposing a fix; "
        "make a narrow change and verify the original failure is resolved."
    ),
    "test-driven-development": (
        "For code changes, define a focused regression check, make the smallest implementation change, then run that "
        "check and relevant existing checks. If tools or dependencies are unavailable, state the unverified part."
    ),
    "grounded-citations": (
        "For research, separate source-backed facts from inference, cite the evidence near each claim, and label "
        "claims that could not be verified."
    ),
    "design-md": (
        "For UI work, follow the existing design tokens and components, check mobile layouts and accessibility, "
        "and keep visual copy limited to what helps the user."
    ),
}

_AGENT_SKILLS = {
    "planner": ("systematic-debugging",),
    "architect": ("systematic-debugging", "test-driven-development"),
    "ui": ("design-md",),
    "frontend": ("design-md", "systematic-debugging", "test-driven-development"),
    "backend": ("systematic-debugging", "test-driven-development"),
    "database": ("systematic-debugging", "test-driven-development"),
    "research": ("grounded-citations",),
    "qa": ("systematic-debugging", "test-driven-development"),
    "security": ("systematic-debugging", "test-driven-development"),
    "devops": ("systematic-debugging", "test-driven-development"),
    "analytics": ("grounded-citations",),
    "voice": (),
}


def for_agent(agent_id: str) -> tuple[list[str], list[str]]:
    names = list(_AGENT_SKILLS.get(agent_id, ()))
    return names, [_SKILLS[name] for name in names]
