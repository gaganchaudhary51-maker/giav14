# GIA dependency and Windows startup repair

Changes:
- Created backend/.venv and installed backend/requirements.txt.
- Startup checks every declared backend package and installed version, plus pip dependency consistency; missing packages trigger installation.
- Corrected npm installation exit-code handling inside the Windows batch block.
- Load backend/.env before app initialization, preserving explicit process environment overrides.
- Declare python-dotenv directly because the application now imports it.
- Default audit logs to the GIA data directory instead of /tmp/gia-audit. Explicit GIA_AUDIT_LOG remains supported. Existing logs are not moved or deleted.
- Use Vite's runner configuration loader for the frontend development launcher, matching the production build.

Verification:
- Backend package consistency: no broken requirements.
- Negative dependency check against the incomplete parent environment correctly identified pytest, pymongo, and numpy as missing.
- Frontend npm dependency tree has all declared direct dependencies; TypeScript/Vite production build passed.
- Initial backend run: 25 failures caused by permission errors on the default audit path; 118 passed.
- After the audit-path fix: 145 passed in 77.08 seconds. One upstream Starlette/httpx deprecation warning remains.
- Started this checkout on http://127.0.0.1:8011 with the production frontend. GET / and /api/health returned HTTP 200; health reports healthy.

Provider status:
- No provider settings found in this checkout's backend/.env or inspected GIA settings locations/process environment.
- No local LLM server responded on the usual loopback ports 11434 and 1234.
- User selected their existing provider; locating its settings is pending. No live model response has been verified.
- Model-dependent tests use mocked responses. The supplied JARVIS concept is not evidence of implemented voice, gesture, or unrestricted autonomous tool execution.
