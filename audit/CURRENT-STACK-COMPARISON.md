# Current GIA v14 / Studio / AI Studio / Hermes comparison

> Historical source comparison. The delivered build follows the later GIA-only direction: selected portable skill procedures and local HRR memory run inside GIA; no Hermes runtime or bridge is shipped.

Audit date: 2026-10-24 (Asia/Kolkata)

## Scope and evidence boundary

Compared the original `giav14-main` folder, the extracted candidate, the Studio slice represented in the candidate/ZIP, and `GIA-hermes-agent-main`. The user-created Google AI Studio app is available through an external project link, but its source/export is not present in the workspace. Its stated 12 agents are therefore user-reported; this audit does not claim to have inspected that app's source or runtime.

## Capability comparison

| Build | Verified contents/capability | Count / evidence | Role in a combined setup |
|---|---|---|---|
| **GIA v14 candidate** | React/TypeScript/Vite UI with a FastAPI workspace API for authentication, projects, plans, approvals, agents, execution surfaces, knowledge, memory, voice, and Studio integrations. | Candidate `/api/agents` returned **12**: planner, architect, ui, frontend, backend, database, research, qa, security, devops, analytics, voice. Auth, profile, project-list, and activity requests all returned HTTP 200 through the Vite proxy. | Recommended user-facing shell and primary dashboard. |
| **Integrated Studio Pods** | Existing candidate `/studio` page manages Studio pods and exposes the call-center demo/integration surfaces. This is a selected Studio slice, not the separate Google AI Studio project. | Candidate `/api/studio/pods` returned **10**: Dr. Ritu Verma, Rahul Sharma, Sophia Cloud Bot, Lucas Growth Engine, Swarn Agent, Boat AI, Social Media Marketing Agent, Google Web Agent, Branding Agent, Graphic Designer Agent. | Keep as the local `/studio` capability; do not label it as the user's 12-agent AI Studio app. |
| **User's Google AI Studio app** | The candidate drawer has a static **My AI Studio — 12 Agents** link that opens the previously observed AI Studio project in a new tab. The link component contains no `fetch`, GIA API import, or `useEffect`. | User reports 12 agents. No exported app files or source roster were found alongside the workspace sources. | Separate linked app until its export is provided and audited; not merged into GIA or Hermes. |
| **Hermes Agent** | Full standalone agent runtime with its own tools, skills, memory/session capabilities, CLI/TUI, web UI, schedulers, subagents, and messaging integrations. | `pyproject.toml`: package `hermes-agent`, version **0.21.3**, Python **>=3.11,<3.14**. Workspace host Python is 3.14.7, outside the declared range. Prior source inventory: 12,808 files excluding dependencies/caches. | Keep as a separate service behind GIA's authenticated adapter; qualify on Python 3.11–3.13. |

## Storage and retrieval detail

- In the 21-Oct `giav14-main`, `backend/app/rag/store.py` and `backend/app/memory/store.py` keep records in process-local dictionaries.
- In the updated ZIP/candidate, the active RAG implementation is under `backend/app/rag/` and persists documents, versions, and chunks through `backend/app/db/sqlite.py`. The active memory store is likewise SQLite-backed and project/user scoped.
- The top-level `rag/README.md` contains only a boundary note; it is not the active RAG implementation. `backend/app/rag/retriever.py` composes lexical RAG and memory lookup.
- ZIP P6 documentation explicitly says Gemini embeddings and cosine-similarity retrieval were not ported. No vector/embedding package, vector table, or vector search implementation appears in executable source. Current search is deterministic lexical term scoring.
- The earlier audit's statement that candidate RAG/memory are process-local was inaccurate for this updated ZIP; it described the 21-Oct folder instead. The two forensic reports above are corrected.

## What is and is not the same

- GIA's 12 internal agent roles and the user's claimed 12 AI Studio agents are different evidence sets. Equal counts do not prove the same agents, prompts, tools, or behavior.
- The candidate's Studio UI currently exposes 10 pods. It is separate from the `/agents` roster and from the external Google AI Studio app.
- The original ZIP is a GIA/selected-Studio assembly with a Hermes integration boundary. It does not contain the complete Hermes runtime or the user's newly created AI Studio project source.
- **My AI Studio — 12 Agents** is only a new-tab link. It does not import code, synchronize data, or call the GIA API.

## Build choice

Use the extracted GIA v14 candidate as the product shell. Keep its 12 core agents and 10 Studio pods distinguishable. Keep Hermes isolated behind the authenticated adapter. Keep the user's AI Studio app linked separately until its exported source can be compared; do not claim an all-in-one code merge from the link alone.

## Verification status

- Candidate automated checks from the earlier release pass: 145 backend tests, 8 HRGen voice tests, Python compilation, TypeScript/Vite production build, and `npm audit` with zero vulnerabilities.
- Latest drawer-component build: **PASS**, 2,368 modules transformed. Build still warns about the 523.27 kB uncompressed Three.js scene chunk.
- Latest local auth/dashboard API path through Vite: login, `/auth/me`, `/projects`, `/events/recent` all HTTP 200.
- Targeted SQLite/RAG/memory/Hermes/provider checks: **23 passed** with a temporary DB and temporary audit log. One Starlette/httpx deprecation warning remains.
- Hermes live bridge, external AI Studio agent behavior, production provider integrations, and deployment are not verified by these local checks.
