# P10 — Original Build & Agent Readiness Audit

**Cycle status: AUDIT COMPLETE; PRODUCT NOT YET READY TO USE**
**Audit basis:** Clean extraction of `GIA-v14-P9-source.zip` in the ChatGPT workspace.
**Scope:** Existing build/startup artifacts, agent registry, UI integration, voice/recording scope, and verification status.
**Important:** This audit inspects the packaged source. It does not claim access to the user's live Windows desktop or a running app.

## Executive summary

The right objective is to configure and start the existing GIA build, use the UI, and verify the twelve agents—not to keep adding features without checking the original product workflow.

The package contains a React + TypeScript + Vite frontend and a FastAPI backend. It includes a Windows verification script (`GIA-VERIFY.ps1`), frontend `package.json` and `package-lock.json`, backend requirements, and explicit release gates.

## Findings

### 1. Existing build and startup

- Frontend source and build configuration exist: `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.ts`, `frontend/src/main.tsx`, and `frontend/src/api.ts`.
- Frontend build command is `npm run build` (TypeScript project build followed by Vite build).
- Vite dev server binds to `127.0.0.1` and proxies `/api` to `http://127.0.0.1:8000`.
- FastAPI app exists at `backend/app/main.py`.
- Windows release check exists at `GIA-VERIFY.ps1`; it runs `npm ci`, `npm run build`, Python `compileall`, and backend pytest, then writes a timestamped report.
- The source package has no `frontend/node_modules` or `frontend/dist`; therefore a production build is not bundled.
- Attempted `npm ci` in this workspace did not complete within the available execution window. No successful frontend production build is claimed.

### 2. The twelve registered agent profiles

`backend/app/agents/registry.py` declares exactly twelve profiles:

1. `planner` — Project Planner
2. `architect` — Software Architect
3. `ui` — UI/UX Agent
4. `frontend` — Frontend Engineer
5. `backend` — Backend Engineer
6. `database` — Database Engineer
7. `research` — Research Agent
8. `qa` — QA Agent
9. `security` — Security Agent
10. `devops` — DevOps Agent
11. `analytics` — Analytics Agent
12. `voice` — Voice Agent

The authenticated `GET /api/agents` route returns registry profiles, and `POST /api/agents/assemble` selects profiles by domains/capabilities. The Agents UI can load and display this registry.

**Critical distinction:** these are registered profiles (role/domain/capability metadata). This audit did not find evidence that each profile is an independently running autonomous agent with its own configured model, tools, credentials, health check, and verified task execution. The separate `backend/app/core/agent_team.py` contains another task-keyword-based team assembly list with a different set of names. These two registries are not a single unified twelve-agent execution system yet.

### 3. UI workflows

- The UI has Home, Projects, Agents, Knowledge, Memory, and Settings.
- The Agents page fetches and displays registry profiles, but does not provide a per-agent run/health/configuration action.
- The plan UI explicitly describes plan creation as planning, not proof of execution.
- Authentication, project selection, RAG indexing/search/history, memory save/search, system status, and Hermes status have UI code paths; they still need browser end-to-end acceptance against a running local instance.

### 4. Voice and recording

- Frontend voice input uses browser `SpeechRecognition` / `webkitSpeechRecognition` where available and submits recognized text as a plan.
- Frontend speech output uses `speechSynthesis`.
- This is not evidence of a raw microphone recording/file-upload pipeline or verified transcription-provider integration. Browser support and microphone permission behavior need testing on the target browser.
- The backend has voice routes/session/provider modules, but live end-to-end voice operation was not verified in this cycle.

### 5. Automated verification

- Re-ran packaged backend tests from the clean extraction: **110 passed in 4.36s**.
- An initial generic `pytest tests` from the project root discovered no tests because the real suite is under `backend/tests`; this was a command-path issue, not a product test failure.
- `npm ci` did not finish in the available workspace execution window; frontend build result remains **NOT VERIFIED**.
- No live Windows UI/browser session, Hermes handoff, or database backup/restore drill was performed.

## P10 decision

**P10 audit is complete. Release status remains NOT READY TO USE.**

The next highest-value cycle is **P11 — One-Click Windows Startup & Setup Reliability**:
1. Inspect the existing Windows launch scripts and README without replacing working pieces.
2. Ensure the launch flow checks prerequisites, starts FastAPI and Vite predictably, and displays useful error messages.
3. Ensure the health check waits for the backend before opening the UI.
4. Keep secrets out of the frontend and avoid exposing local services publicly by default.
5. Document one simple, non-technical startup path and a one-click diagnostic report.
6. Verify script syntax/static behavior here; final execution still must be accepted on the user's Windows PC if this workspace cannot run Windows.

After P11, proceed to **P12 — Twelve-Agent Readiness Matrix and unified registry**: define per-agent model/tool/configuration/permissions/health/acceptance criteria, reconcile the two registries, then test agents individually and in orchestration. Do not label profiles as working agents until their real execution is proven.

## Evidence files reviewed

- `AGENTS.md`
- `agents/README.md`
- `backend/app/agents/registry.py`
- `backend/app/routes/agents.py`
- `backend/app/core/agent_team.py`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/src/main.tsx`
- `FINAL-READINESS.md`
- `BUILD-LOG.md`
- `GIA-VERIFY.ps1`
