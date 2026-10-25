# Universal Agent Pods & Multi-Channel Studio — Implementation Report

## Scope delivered in this source update
- Preserved the existing project/root name `giav14-main` and existing folders.
- Added the Studio UI section and direct `/studio` path support.
- Added ten configurable pod profiles requested for reception, sales, WhatsApp, SEO/GEO/AEO, financial auditing, e-commerce, social media, web indexing, branding, and graphic design.
- Added tenant-scoped SQLite configuration tables for pod prompt, selected model, channels, enabled state, and prompt-evolution proposals. These are new tables; existing RAG and memory tables/records are not read, migrated, rewritten, or deleted.
- Added `/api/studio/pods`, `/api/studio/pods/{pod_id}`, `/api/agent/evolve` (under `/api/studio/agent/evolve`), evolution review endpoints, and a demo call-center HUD endpoint.
- Added a split-screen call-center demo view with transcript examples, customer-history placeholder, recommended scripts, and queue timers. Data is explicitly labeled demo; no real customer data or telephony is connected.
- Added optional Supabase server-side mirror for Studio configuration and approved prompt changes and SQL schema at `backend/sql/studio_pods_supabase.sql`.
- Added SIM-less VoIP webhook scaffolding with HMAC signature verification, provider-configuration status endpoint, and transcript event acknowledgment.
- Added WhatsApp template rendering with variable allowlisting. Rendering does not send messages.
- Added responsive slate/navy/teal Studio styling and mobile bottom navigation with a central dashboard button.
- Added operational-only policy copy excluding LIMS accession codes, tube/vial processing, sample tracking, lab-record interpretation, symptoms, and clinical advice.

## Verification
- Backend full suite: **135 passed**.
- New Studio/telephony focused tests: **9 passed** (included in full suite).
- Python route modules imported during test execution.
- ZIP integrity is to be checked for the release packages.

## Explicitly not complete / not claimed
- Frontend production build could not be verified in this workspace: `npm ci` stalled/interrupted and left incomplete `node_modules`; `npm run build` then failed because TypeScript type packages were missing. This is an environment/dependency-install failure, not a passing frontend build.
- No real Gemini API call was made; `GEMINI_API_KEY` is required. Gemini 1.5 Flash model availability should be verified with the chosen account/provider before production.
- No Supabase URL/key was configured, so remote persistence was not live-tested. Without Supabase config, local SQLite remains the persistence mode.
- No VoIP DID/SIP provider, signed vendor callback, Groq STT API call, Kokoro TTS service, or WhatsApp Business API was connected or tested.
- Model names Kore/Fenrir/Zephyr/Puck are selectable config values only; corresponding live audio engine adapters are not yet implemented.
- The call-center history, transcript, scripts, and queue shown in the UI are demo data, not live customer operations.
- Cost below ₹0.50/minute is not verified or guaranteed. Vendor billing, region, audio duration, and hosting costs must be measured.
- No autonomous prompt rewrite is applied silently. Gemini output is stored as a pending proposal; a signed-in user must approve it before the active prompt changes.
- The system is not yet production-ready. Perform a clean `npm ci`, `npm run build`, Windows startup, live provider acceptance, webhook signature validation with vendor test events, and backup/restore drills.

## Configuration
See `.env.example` for optional keys. Keep secrets only in backend environment variables, never in frontend `.env` or release archives. Supabase service-role key must remain server-side.
