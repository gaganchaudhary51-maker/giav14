# P11 — One-Click Windows Startup & Setup Reliability

**Cycle status: IMPLEMENTED IN SOURCE; WINDOWS RUNTIME ACCEPTANCE PENDING**

## Goal
Make local startup understandable for a non-technical user while preserving the existing GIA project layout and keeping services private to the local computer.

## Changes
- Added `START-GIA.bat` as the single entry point.
- Added `RUN-GIA-BACKEND.bat` and `RUN-GIA-FRONTEND.bat` so service windows have simple titles and useful exit messages.
- Launcher checks the GIA project marker and availability of Python, Node.js, and npm.
- Creates `backend/.venv` if absent and installs backend requirements only when FastAPI/Uvicorn cannot be imported.
- Runs `npm ci` only when the Vite install is missing, using the checked-in lockfile.
- Starts FastAPI and Vite bound to `127.0.0.1` only.
- Waits for `/api/health` to return `healthy` before opening the browser.
- Added `P11-STARTUP-GUIDE.md` with user-facing startup and troubleshooting instructions.

## Verification performed in this workspace
- Reviewed the source project's backend health route: `GET /api/health` returns `{"status":"healthy"}`.
- Re-ran backend suite from the extracted source: **110 passed in 3.44 seconds**.
- Reviewed launcher paths against the existing project layout, package-lock, requirements file, Vite proxy, and health route.
- Confirmed launch commands bind to loopback (`127.0.0.1`), not the LAN/public interface.
- ZIP packaging integrity is checked after generation.

## Not verified / release gates
- Windows batch execution itself could not be run in this Linux workspace. The user's Windows machine must confirm first-run setup, both service windows, health wait, and browser opening.
- Frontend `npm ci` and `npm run build` were not rerun successfully in this cycle; production build remains unverified.
- This is a local development startup helper, not a production installer or Windows service.
- Startup does not prove all UI workflows, the 12 agents, voice, Hermes live handoff, or backup/restore work.

## Decision
P11 startup helper is implemented and statically reviewed, but it is not marked fully accepted until a Windows smoke test is performed. Continue to P12 only after the user confirms the next cycle.
