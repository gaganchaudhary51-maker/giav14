# P2 Implementation Report — Durable Local Persistence

## Status
P2 is implemented in the working copy under `files/giav14-main`.

## What changed
- Added a shared SQLite connection helper (`backend/app/db/sqlite.py`) with WAL mode and a configurable `GIA_DATA_DIR`.
- Projects and users now use SQLite when MongoDB is not configured or reachable; MongoDB remains supported.
- RAG chunks and project-scoped memory records are persisted in SQLite and loaded back when a store is recreated / the API process restarts.
- Added database indexes for user email and user/project scoped RAG and memory lookup.
- Expanded `/api/system/persistence` to report the active store types and database path while preserving the legacy `backend` field for API compatibility.
- Added regression tests for SQLite durability and user/project isolation.

## Verification
- Backend test suite: **83 passed** in this workspace.
- The tests used a temporary `GIA_DATA_DIR`, so they did not touch the default local data directory.
- Frontend production build is still a separate release gate; dependency installation was not verified in this workspace.

## Local data location
By default, SQLite data is stored in `backend/data/gia.sqlite3`. Set `GIA_DATA_DIR` to choose a different directory. Keep this database out of source control and back it up if it contains important user data.

## Remaining work / safety notes
- `production_ready` intentionally remains `false`: production deployment still needs backup/restore validation, secrets and deployment configuration review, and end-to-end checks.
- This is local SQLite durability, not a multi-host database architecture. For multi-instance deployments, configure and operate MongoDB.
- Existing in-memory global-memory, event/audit, task, and execution subsystems still need an inventory and persistence migration before claiming every GIA subsystem is durable.
- Hermes and HRGen AI Studio are still audited source inputs, not merged runtime services. Their selective adapters remain a later phase.
