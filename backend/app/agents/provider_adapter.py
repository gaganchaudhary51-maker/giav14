"""Opt-in OpenAI-compatible text-model adapter for GIA agent profiles.

This adapter intentionally does not read or retrieve personal RAG/memory data.
Only the explicit prompt supplied by an authenticated caller is sent to the configured provider.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from app.agents.registry import AGENTS

_SKILL_DOMAINS = {
    "planner": ("ai",), "architect": ("ai", "backend"), "ui": ("ui_ux",),
    "frontend": ("frontend",), "backend": ("backend",), "database": ("database",),
    "research": ("research",), "qa": ("qa",), "security": ("security",),
    "devops": ("devops",), "analytics": ("analytics",), "voice": ("ai",),
}


def skill_guidance(agent_id: str) -> list[str]:
    """Return concise GIA agent and RAG skills for prompt guidance; never grants tools."""
    from app.agents.registry import agent_registry
    from app.skills.registry import skill_registry
    from app.skills.portable_guidance import for_agent

    canonical = agent_registry.canonical_id(agent_id)
    if canonical is None:
        raise ValueError("Unknown agent ID")
    # Every provider-backed agent should carry QA and RAG guardrails, in
    # addition to its role-specific skill domains.
    domains = list(dict.fromkeys((*_SKILL_DOMAINS.get(canonical, ()), "qa", "rag")))
    skills = []
    for domain in domains:
        skills.extend(item["skill"] for item in skill_registry.for_domain(domain))
    portable_names, _ = for_agent(canonical)
    skills.extend(portable_names)
    # Skill labels are reasoning guidance only; this chat adapter has no tools.
    return [skill for skill in dict.fromkeys(skills) if skill != "tool-use"][:24]


@dataclass(frozen=True)
class ProviderConfig:
    enabled: bool
    base_url: str
    model: str
    api_key: str
    timeout_seconds: float = 30.0


def get_config() -> ProviderConfig:
    raw_enabled = os.getenv("GIA_AGENT_PROVIDER_ENABLED", "").strip().lower()
    base_url = os.getenv("GIA_AGENT_BASE_URL", "").strip().rstrip("/")
    parsed = urlparse(base_url)
    local_ollama = parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost", "::1"} and parsed.port == 11434
    return ProviderConfig(
        enabled=raw_enabled in {"1", "true", "yes", "on"},
        base_url=base_url,
        model=os.getenv("GIA_AGENT_MODEL", "").strip(),
        api_key=os.getenv("GIA_AGENT_API_KEY", "").strip(),
        timeout_seconds=180.0 if local_ollama else 30.0,
    )


def config_problem(config: ProviderConfig) -> str | None:
    if not config.enabled:
        return "provider_disabled"
    if not config.base_url or not config.model or not config.api_key:
        return "provider_configuration_incomplete"
    parsed = urlparse(config.base_url)
    if parsed.scheme != "https" and parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        return "base_url_must_use_https_or_loopback"
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "invalid_base_url"
    return None


def runtime_status() -> dict[str, Any]:
    config = get_config()
    problem = config_problem(config)
    return {
        "provider": "openai-compatible",
        "enabled": config.enabled,
        "configured": problem is None,
        "model": config.model or None,
        "agent_ids": [a.id for a in AGENTS],
        "ready_for_live_calls": problem is None,
        "reason": problem,
        "personal_memory_attached": False,
        "tool_execution_enabled": False,
    }


def invoke(
    agent_id: str,
    prompt: str,
    conversation_history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Send a project-scoped conversation turn; no tools or implicit memory are attached."""
    from app.agents.registry import agent_registry

    canonical = agent_registry.canonical_id(agent_id)
    if canonical is None:
        raise ValueError("Unknown agent ID")
    if not isinstance(prompt, str) or not prompt.strip() or len(prompt) > 12000:
        raise ValueError("Prompt must contain 1-12000 characters")
    config = get_config()
    problem = config_problem(config)
    if problem:
        raise RuntimeError(problem)

    agent = agent_registry.get(canonical)
    skills = skill_guidance(canonical)
    from app.skills.portable_guidance import for_agent
    _, portable_rules = for_agent(canonical)
    portable_prompt = "\n".join(f"- {rule}" for rule in portable_rules)
    messages = [
        {"role": "system", "content": (
            f"You are the GIA {agent['role']} agent. Help with the user's current request and "
            "maintain the conversation context. You have no tools. Use only the project context "
            "explicitly included in the latest user message; do not claim to have changed or "
            "verified files unless evidence is included. Do not access or imply personal memory; "
            "personal memory and tool execution are disabled for this call. Apply these GIA agent and RAG skills "
            "as reasoning guidance only: " + ", ".join(skills) + "."
            + ("\nImported portable agent procedures:\n" + portable_prompt if portable_prompt else "")
        )}
    ]
    history = conversation_history or []
    if not isinstance(history, list) or len(history) > 20:
        raise ValueError("Conversation history must contain at most 20 messages")
    for item in history:
        if not isinstance(item, dict):
            raise ValueError("Conversation history contains an invalid message")
        role = item.get("role")
        content = item.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str) or len(content) > 12000:
            raise ValueError("Conversation history contains an invalid message")
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": prompt.strip()})
    body = {
        "model": config.model,
        "messages": messages,
        "stream": False,
    }
    request = urllib.request.Request(
        config.base_url + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": "Bearer " + config.api_key,
                 "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"provider_http_error_{exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise RuntimeError("provider_connection_failed") from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("provider_invalid_response") from None

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("provider_response_missing_content") from None
    if not isinstance(content, str):
        raise RuntimeError("provider_response_missing_content")
    return {"agent_id": canonical, "provider": "openai-compatible",
            "model": config.model, "status": "COMPLETED", "output": content,
            "personal_memory_attached": False, "tools_invoked": []}
