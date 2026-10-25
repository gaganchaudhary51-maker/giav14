# Three-source audit: GIA v14, Hermes Agent, HRGen AI Studio

Audit date: 2026-10-21  
Basis: the three archives uploaded in this conversation. This is a source/configuration audit, not a claim that every service was launched and end-to-end tested.

## Executive decision

Use **GIA v14 as the product shell and FastAPI control plane**. Keep Hermes isolated as the agent runtime. Port selected HRGen Studio RAG/memory capabilities behind tested Python interfaces. Do not combine all three frontends, package environments, or persistence stores directly.

## GIA v14 — `giav14-main.zip`

### Confirmed structure
- FastAPI application: `backend/app/main.py`.
- API routes include auth, projects, conversation planning, tasks, agents, approvals, audit, events, memory, global memory, RAG, voice, execution, verification, workspace and builder modules.
- React/TypeScript/Vite frontend is small: `frontend/src/main.tsx`, `api.ts`, `styles.css`, and `vite.config.ts`.
- Backend tests in the supplied source were executed in this environment: **80 passed**.

### Important implementation gaps
- `backend/app/rag/store.py`: `RAGStore` stores chunks in a Python dictionary (`self._items`).
- `backend/app/memory/store.py`: `MemoryStore` stores memories in a Python dictionary (`self._items`).
- `backend/app/db/store.py` and `backend/app/db/user_store.py`: MongoDB is optional via `MONGO_URL`; if it is absent or connection fails, stores fall back to process memory.
- `/api/system/persistence` checks the project repository store; it does not prove that users, tasks, events, RAG and memory are all durable.
- `backend/app/routes/conversation.py` returns `status: planned`; `/conversation/plan` is a plan-generation endpoint, not proof that a task was executed.
- Before this P1 update, most frontend navigation destinations showed the same generic placeholder content.
- Vite ran on port 5173 while the API ran on port 8000; the original API client used a hard-coded `http://localhost:8000/api`, creating a browser cross-origin/CORS risk if CORS is not enabled.

### Decision
Keep the FastAPI routes and governance as the primary API. Add durable repository implementations before using RAG/memory for important personal data. Build the frontend against the existing API first, and label planning versus execution accurately.

## Hermes Agent — `GIA-hermes-agent-main.zip`

### Confirmed structure
- Archive contains 14,641 entries.
- `pyproject.toml` identifies Hermes Agent version `0.21.3`.
- Declared Python range is `>=3.11,<3.14`; Python 3.14 is outside the declared support range.
- Source contains broad tool and runtime infrastructure, including `tools/registry.py`, `tools/memory_tool.py`, `tools/session_search_tool.py`, `tools/terminal_tool.py`, skill management and MCP-related modules.
- Archive also contains a substantial web dashboard under `web/`.

### Integration risks
- Hermes is a full runtime, not a library to indiscriminately copy into the GIA backend.
- Tool execution, shell/filesystem access, network access, MCP servers, skills and credentials require their own permissions, timeouts, allowlists and audit events.
- The current Windows environment uses Python 3.14.7, so do not install Hermes into GIA's existing `.venv`.

### Decision
Run Hermes in a separate Python 3.13 environment/service. GIA FastAPI should call it through an authenticated adapter with a typed request/response schema, timeout/cancellation handling and permission checks. The browser must not call Hermes directly.

## HRGen AI Studio — `HRGen_AI_Studio.zip`

### Confirmed source files
- `server/lib/ragEngine.js`
- `server/lib/ragLibraryStore.js`
- `server/lib/giaMemoryStore.js`
- `server/lib/universalMemory.js`
- `gia-service/lib/studioClient.js`

### Useful capabilities to selectively port
- RAG document chunking and retrieval scoring with source metadata.
- JSON-backed library/document records and version-related metadata.
- Conversation transcripts, rolling summaries and shared-memory concepts.

### Risks
- The archive includes populated `.env` files at `HRGen_AI_Studio/.env` and `HRGen_AI_Studio/gia-service/.env`, with credential-like non-empty values. Treat them as exposed: rotate/revoke real credentials and do not distribute these `.env` files.
- Hard-coded launcher paths and default login configuration must be reviewed before reuse.
- The archive does not include a root `package.json`/lockfile sufficient for reproducing the whole Studio installation from this archive alone.
- HRGen JSON data paths and the GIA FastAPI stores are not automatically the same database or compatible schema.
- Do not import private memory data without a reviewed migration, record counts, user/workspace ownership mapping and explicit confirmation.

### Decision
Port behavior, not the whole Node application. Reimplement or adapt RAG/memory behind Python repository/service interfaces, then test persistence, user/project isolation, export and deletion. Keep Studio's actual data separate until a migration is validated.

## Unified target

```text
React + TypeScript + Vite
          |
          | same-origin /api
          v
GIA FastAPI (auth, projects, orchestration, approvals, audit)
          |
          +---- SQLite repositories (initial canonical storage)
          |
          +---- RAG service (source metadata + lexical search; vector adapter later)
          |
          +---- Memory service (user/workspace/project scoped)
          |
          +---- Hermes adapter (separate Python 3.13 service)
```

## Release gates

1. **P1 UX/API foundation:** canonical navigation, first-run intro, responsive screens, API proxy, truthful status and empty/error states. Included in the accompanying P1 update.
2. **P2 persistence:** migrations, backup/restore, restart persistence, user isolation, memory export/delete.
3. **P3 execution:** a real task lifecycle from plan to execution and verification; approvals for risky actions.
4. **P4 RAG/memory:** indexing, retrieval, source citations, durable personal memories, deletion and isolation tests.
5. **P5 Hermes:** isolated runtime, authenticated adapter, tool permissions, timeouts and audit records.
6. **P6 release:** end-to-end tests, production `/api` reverse proxy, secrets scan, backup/restore drill and accessibility review.

## Verification truth table

| Claim | Current evidence |
|---|---|
| GIA backend unit/API tests pass | Yes: 80 tests passed in this environment |
| Updated frontend production build passes | Not yet verified here; dependency install did not complete in this environment |
| GIA RAG is durable | No: current store is process-memory based |
| GIA Memory is durable | No: current store is process-memory based |
| `/conversation/plan` executes a task | No: it returns a plan status |
| Hermes runs on current Python 3.14 | Unsupported by its declared Python range |
| Studio credentials are safe to redistribute | No: rotate real values and exclude `.env` files |
| All three are already integrated | No: integration remains a phased engineering task |
