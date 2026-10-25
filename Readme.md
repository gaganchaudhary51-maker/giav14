

GIA Universal AI is a modular AI-agent workspace with a React/Vite web client and a FastAPI backend. The repository includes agent and orchestration modules, model routing, governance and approval flows, workspace and sandbox APIs, memory and retrieval components, skills, and automated backend tests.

> **Project status:** This repository contains an actively developed application. Provider integrations, persistent storage, authentication settings, and production deployment must be configured and verified for the environment where you run it. A successful local startup does not by itself establish production readiness.

## Repository layout

| Path | Purpose |
| --- | --- |
| `backend/` | FastAPI application, API routes, repositories, and backend tests |
| `frontend/` | React 19 and Vite web client |
| `agents/`, `router/`, `builder/` | Agent modules, routing, and builder components |
| `rag/`, `knowledge/`, `memory/` | Retrieval, knowledge, and memory components |
| `skills/` | Skill definitions and related application resources |
| `sandbox/` | Sandboxed execution components |
| `GOVERNANCE/` | Project blueprint, security baseline, and governance documents |
| `docs/` | Local run, acceptance, and architecture guidance |
| `tests/` | Project-level tests |
| `GIA-VERIFY.ps1` | Windows verification script |

## Requirements

- Python 3.10 or newer
- Node.js and npm
- MongoDB for persistent project storage; without a configured database, some storage paths may use an in-memory fallback

## Quick start

```bash
git clone https://github.com/gaganchaudhary51-maker/giav14.git
cd giav14
```

### Configure environment

Copy `.env.example` to `.env` and set values appropriate for your local environment. Do not commit real credentials.

The example file documents:

- `GIA_AUTH_SECRET` — secret used by authentication features
- `MONGO_URL` — MongoDB connection string
- `MONGO_DB` — database name (defaults to `gia` in the example)
- `GIA_WORKSPACE_ROOT` — workspace directory used by the application

Use a long, unique authentication secret and keep production secrets in your deployment platform's secret manager.

### Start the backend

From the repository root:

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\\Scripts\\Activate.ps1
```

Install backend dependencies and start the API:

```bash
pip install -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`; interactive API documentation is at `http://localhost:8000/docs`.

### Start the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite. To test from a mobile device on the same network, follow the Vite host/network instructions and the guidance in [docs/LOCAL-RUN.md](docs/LOCAL-RUN.md).

## Verification

Run backend tests:

```bash
cd backend
pytest -q
```

Build the frontend:

```bash
cd frontend
npm ci
npm run build
```

On Windows, the repository also includes a combined verification script:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\GIA-VERIFY.ps1
```

The script checks available runtimes, installs frontend dependencies, builds the frontend, runs backend tests, and writes a timestamped report. Review the report and any warnings; local automated checks do not verify external model credentials, production database connectivity, deployment configuration, or every browser/device combination. See [RUN-GIA-VERIFY.md](RUN-GIA-VERIFY.md) for details.

## Security and deployment

- Keep `.env` and all real credentials out of version control.
- Review [GOVERNANCE/SECURITY-BASELINE.md](GOVERNANCE/SECURITY-BASELINE.md) and [GOVERNANCE/AGENT-GOVERNANCE.md](GOVERNANCE/AGENT-GOVERNANCE.md) before exposing the service.
- Configure persistent storage and production authentication before handling durable user data.
- Treat the in-memory persistence fallback as non-durable.
- Require appropriate approval and audit controls for sensitive actions.
- Verify the deployment environment, provider configuration, and data handling before using the application with real users or data.

## Project guidance

- [Local setup](docs/LOCAL-RUN.md)
- [Acceptance matrix](docs/ACCEPTANCE-MATRIX.md)
- [Agent governance](docs/AGENT-GOVERNANCE.md)
- [Master blueprint](GOVERNANCE/MASTER-BLUEPRINT.md)
- [Security baseline](GOVERNANCE/SECURITY-BASELINE.md)
- [Third-party notices](THIRD-PARTY-NOTICES.md)

## License

No root-level license file is currently included. Check with the repository owner before redistributing or using this project under an assumed open-source license.
