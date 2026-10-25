# GIA Content Rules & Product Messaging

## Voice
- Clear, calm, direct, helpful; avoid grandiose “fully autonomous” or “does everything” claims.
- Explain unfamiliar terms briefly. Prefer task-oriented labels over internal architecture jargon.
- Tell the user what happened, what did not happen, and what action is needed next.

## Truthfulness
- Use “plan created” for a planning response; use “executed” only when an execution record proves it.
- Use “verified” only when a verification result exists and is successful.
- Show integration states as Connected, Disconnected, Not configured, or Error based on live evidence.
- Do not describe an external provider or integration as live/connected without a successful connection check.
- Describe retrieval as lexical search unless semantic embeddings are actually configured and tested.
- Never claim Ready to Use / production-ready while blocking gates are open.

## Privacy and security
- Never put credentials, API keys, access tokens, personal data, or real client content in demo copy or screenshots.
- Do not promise absolute privacy or security. State the actual project/user scoping and deployment requirements.
- Recommend fictional sample data for demonstrations.
- Keep production secrets out of source, archives, logs, and reports.

## UX writing
- Every primary action should have a specific verb: Create project, Create plan, Index knowledge, Search knowledge, Save memory, Search memory.
- Pair empty states with a useful next action.
- Errors should say what failed and how to recover, without leaking stack traces or secrets.
- Distinguish status, result, and next action visually.
- Keep onboarding to three steps: choose a project, describe a goal, review and verify.

## Live demo rules
- Use a disposable account and synthetic content.
- State limitations before demonstrating an optional integration.
- Show at least one successful result and one status/verification surface.
- If a check fails, state it plainly and do not improvise a success claim.
