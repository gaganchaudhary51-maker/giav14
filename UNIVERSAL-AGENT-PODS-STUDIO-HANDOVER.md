# GIA v14 — Universal Agent Pods & Multi-Channel Studio Handover

## Preserve these names
- Project root inside release ZIP: `giav14-main`
- Existing project and source folder names are unchanged.
- Feature report: `UNIVERSAL-AGENT-PODS-STUDIO-REPORT.md`

## What changed
- Frontend: `frontend/src/main.tsx`, `frontend/src/api.ts`, `frontend/src/styles.css`
- Backend: `backend/app/routes/studio.py`, `backend/app/routes/telephony.py`, `backend/app/main.py`
- Tests: `backend/tests/test_studio.py`
- Config template: `.env.example`
- Optional Supabase schema: `backend/sql/studio_pods_supabase.sql`
- Dependency declaration: `backend/requirements.txt`

## API endpoints
- `GET /api/studio/pods` — ten tenant-scoped pod profiles/configs
- `PUT /api/studio/pods/{pod_id}` — update prompt, selected model, channels, enabled state
- `POST /api/agent/evolve` (also available under `/api/studio/agent/evolve`) — request Gemini prompt proposal; requires configured `GEMINI_API_KEY`
- `POST /api/agent/evolve/{proposal_id}/review` (also under `/api/studio/agent/evolve/{proposal_id}/review`) — approve/reject; active prompt changes only on approval
- `GET /api/agent/evolve/pending` (also under `/api/studio/agent/evolve/pending`) — pending prompt proposals
- `GET /api/studio/call-center/demo` — explicitly demo-only transcript/queue data
- `GET /api/telephony/providers` — integration configuration status
- `POST /api/telephony/webhooks/voip/incoming` — HMAC-protected webhook scaffold
- `POST /api/telephony/webhooks/voip/transcript` — HMAC-protected transcript event acknowledgment
- `POST /api/telephony/whatsapp/template/render` — allowlisted template render only; does not send

## Local verification
- Backend suite: 135 passed.
- Python compile check: passed.
- Frontend production build: NOT VERIFIED. `npm ci` was interrupted in this workspace and left incomplete dependencies; `npm run build` reported missing TypeScript type packages. Run clean `npm ci` then `npm run build` on a network-enabled machine before deploying.

## Optional integrations
Configure backend environment variables from `.env.example` only on the server:
- Gemini: `GEMINI_API_KEY`, `GEMINI_MODEL`
- Supabase mirror: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STUDIO_PROMPTS_TABLE`
- VoIP webhook: `GIA_VOIP_PROVIDER`, `GIA_VOIP_WEBHOOK_SECRET`
- Groq STT: `GROQ_API_KEY`
- Kokoro service: `KOKORO_TTS_URL`
- WhatsApp Business: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`

No secret values are included in this package. Apply the Supabase SQL manually before configuring the mirror. Keep service-role keys backend-only.

## Not yet production-ready
The selected Kore/Fenrir/Zephyr/Puck model value is configuration metadata only; live adapters are pending. Live VoIP vendor call control, audio streaming, Groq transcription, Kokoro synthesis, WhatsApp delivery, Supabase live persistence, customer-history integration, cost-per-minute, Windows startup and frontend build remain unverified. Demo customer history and queue values are not real. The system intentionally does not interpret medical data or provide clinical advice.
