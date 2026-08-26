# Security baseline

Repo is currently public. Make it private before adding real keys or tenant data.

## Required now
- Set GIA_AUTH_SECRET in the environment. Do not use the code default `dev-only-change-me` in any real run.
- Keep `.env` out of git.
- Mongo URL and API keys live in host env or GitHub Actions secrets only.
- Tokens are HMAC session tokens. Production should move to a real session store.

## Builder / sandbox
- Sandbox allows only `python` and `pytest` with timeout.
- Sensitive builder jobs require approval.
- Workspace must stay under GIA_WORKSPACE_ROOT.

## Do not
- Commit knowledge/memory with personal or patient data
- Import old Drive zip packs over this V14 tree
- Claim DEPLOYED or VERIFIED without evidence
