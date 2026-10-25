# GIA v14 — Simple Windows Startup

## For the user
1. Extract the final GIA ZIP into a normal folder (not inside another ZIP).
2. Open that folder and double-click `START-GIA.bat`.
3. On the first run, the launcher may install Python and Node dependencies. Internet access is required for this first-time setup.
4. Keep the **GIA Backend** and **GIA Frontend** terminal windows open while using GIA.
5. The browser opens at `http://127.0.0.1:5173/` after the backend health endpoint responds.
6. To stop GIA, close both service windows.

## Safety
- Backend and Vite bind to `127.0.0.1` only; this launcher does not expose the app to the LAN or internet.
- The launcher does not generate, print, or embed provider credentials.
- If startup fails, read the message in the launcher and the **GIA Backend** / **GIA Frontend** windows.
- Do not share `.env` files, tokens, or local database files when requesting help.

## What the launcher verifies
- The project root marker exists.
- Python, Node.js, and npm are available.
- The backend virtual environment exists and can import FastAPI/Uvicorn; otherwise it creates/installs it.
- Vite is installed; otherwise it runs `npm ci` using the lockfile.
- The backend `/api/health` endpoint reports `healthy` before opening the browser.

## Important limits
This launcher is a development/local-use startup helper, not a production installer or Windows service. A passing startup does not prove every page, agent, voice feature, Hermes connection, or backup/restore workflow is operational. Those need separate acceptance tests.
