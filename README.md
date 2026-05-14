# Document Q&A (Docker + OpenAI)

Full-stack RAG app: upload `.txt`, `.pdf`, or `.docx`, ask questions grounded in the document. **Chat is only kept in browser memory** — refresh clears messages and the selected document. Document text and embeddings are stored in PostgreSQL (pgvector).

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) with Compose v2
- An [OpenAI API key](https://platform.openai.com/api-keys)

## Quick start

1. Copy environment file and add your key:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY`.

2. Build and run:

   ```bash
   docker compose up --build
   ```

3. Open the UI at [http://localhost:8080](http://localhost:8080). The API is also exposed at [http://localhost:8000](http://localhost:8000) (e.g. `GET http://localhost:8000/api/health`).

## Architecture

- **web**: Nginx serves the Vite build and proxies `/api/*` to the API.
- **api**: FastAPI — `POST /api/documents` (multipart), `POST /api/chat` (JSON), `GET /api/health`.
- **db**: PostgreSQL 16 with pgvector for chunk embeddings.

Optional env vars: `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL` (defaults in `.env.example`).

## Local development (without Docker for the app shell)

- **Backend**: `cd backend`, create a venv, `pip install -r requirements.txt`, set `DATABASE_URL` and `OPENAI_API_KEY`, run `uvicorn app.main:app --reload`.
- **Frontend**: `cd frontend`, `npm install`, `npm run dev` — Vite proxies `/api` to `http://127.0.0.1:8000`.

## Ephemeral chat

There is **no** `messages` table and **no** `localStorage` / `sessionStorage` for chat. Only React state holds the thread; a full page reload starts over (per product default in this repo).
