# GIA Frontend

## Development

The Vite development server listens on `127.0.0.1:5173`. Calls to `/api/*` are proxied to the FastAPI server at `http://127.0.0.1:8000` by `vite.config.ts`.

Start FastAPI separately, then run the frontend's `npm run dev`.

## API configuration

`VITE_API_URL` defaults to `/api`. Keep it relative during local development so the browser uses the Vite proxy and avoids cross-origin requests. In production, configure the web server/reverse proxy to route `/api` to FastAPI.

## Current feature boundaries

- Chat creates a plan using `/conversation/plan`; this is not full task execution.
- Knowledge indexes pasted text using the current GIA RAG API.
- Memory stores project-scoped notes using the current GIA memory API.
- The current RAG and memory stores are in-memory and can reset on backend restart. Do not treat them as durable storage until the P2 persistence migration is complete.
