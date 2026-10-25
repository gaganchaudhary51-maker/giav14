# Release verification

- Backend + syntax: `python scripts/verify-release.py`
- Optional integration status/live LLM test: `python scripts/live-integration-smoke.py`
- Frontend build: `cd frontend && npm ci && npm run build`
- `.env.example` lists optional variables; never commit credentials.
- `.github/workflows/ci.yml` builds backend and frontend in CI.
- WhatsApp tests do not send real messages. VoIP HMAC local tests do not prove live call/audio functionality.
