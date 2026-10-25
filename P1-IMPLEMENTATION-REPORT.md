# GIA v14 + Hermes + HRGen AI Studio — Architecture & P1 Implementation

Date: 2026-10-21

## What was changed in this P1 build

This build focuses on the user-facing foundation and a consistent route/API boundary.

- Added a first-run introduction shown once per browser, with a way to replay it from Settings.
- Replaced the generic placeholder module view with distinct Projects, Agents, Knowledge/RAG, Memory, and Settings screens.
- Kept one canonical navigation entry per feature. The duplicate generic Files navigation item is removed from the main navigation.
- Added project selection to the persistent sidebar so actions are explicitly scoped to one project.
- Added real UI calls for the existing GIA endpoints: agent registry, RAG index/search, memory add/search, API health and project-store persistence status.
- Renamed the chat action to “Create plan” and explicitly display that a plan is not proof of execution.
- Added user-facing warnings that current GIA RAG and Memory stores are in-memory and may reset after a backend restart.
- Changed the frontend API default to relative `/api` and added a Vite development proxy to `http://127.0.0.1:8000`, avoiding the common browser CORS mismatch between ports 5173 and 8000.
- Improved responsive layouts, focus states, empty states, errors, and consistent visual components.

## Verification

- Backend test suite executed from the supplied GIA v14 source: **80 passed**.
- Updated TypeScript/TSX files passed TypeScript transpilation syntax checks. A full frontend production build could not be independently verified here because npm dependency installation did not complete; this ZIP intentionally excludes `node_modules`. The original supplied project had previously built successfully on the user's PC before these P1 UI changes. Full build verification remains a release gate.
- Hermes and HRGen Studio were source-reviewed only; no claim is made that their runtimes were installed or end-to-end tested here.

## Known limitations — not hidden

1. GIA's `RAGStore` and `MemoryStore` currently keep items in process memory. Restarting the API loses those records.
2. The project/user stores fall back to process memory when MongoDB is not configured. `/api/system/persistence` reports the project repository's state only; it is not a complete persistence health check for every store.
3. `/api/conversation/plan` creates a plan and returns `status: planned`; it does not by itself execute the task.
4. The P1 RAG screen indexes pasted text. File upload/parsing, embeddings/vector search, source citations and document lifecycle are later work.
5. The P1 Memory screen writes notes to the current in-memory GIA memory API. It does not import data from HRGen Studio, Hermes, another GIA installation, or an older database.
6. The Vite proxy applies to development. A production deployment must configure its reverse proxy/server to route `/api` to FastAPI.
7. This P1 build does not bundle Hermes or HRGen Studio code into the Python service. They remain separate source projects until their adapters and persistence migration are designed and tested.

## Run model

- Frontend dev server: Vite at `http://127.0.0.1:5173`
- Main API: FastAPI at `http://127.0.0.1:8000`
- Frontend calls relative `/api/...`; Vite proxies those calls to FastAPI in development.

## P2 acceptance criteria

- SQLite schema/migrations and repository interfaces for users, projects, sessions, tasks, events, RAG documents/chunks and personal memory.
- Existing in-memory records are not silently discarded during migration; export/import path is documented.
- Restart test proves records survive API restart.
- User/workspace/project scoping tests prove private memory cannot leak between users/projects.
- Backup, restore and deletion/export tests exist before personal data is used for real.

## Security notes

The HRGen AI Studio archive contains populated environment files and credential-like values. Treat them as exposed, rotate/revoke them, and remove real `.env` files from distributable archives. Keep only `.env.example` placeholders in source packages. Do not paste secrets into chat.
