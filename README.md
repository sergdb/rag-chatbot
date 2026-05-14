# Document Q&A (OpenAI + Postgres)

Full-stack RAG app: upload `.txt`, `.pdf`, or `.docx`, ask questions grounded in the document. **Chat is only kept in browser memory** — refresh clears messages and the selected document. Document text and embeddings are stored in PostgreSQL (pgvector extension required).

## Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.12+ on your `PATH` (use a venv if you prefer; the `api` script uses `python`)
- **PostgreSQL** with the **[pgvector](https://github.com/pgvector/pgvector)** extension enabled, and a database (e.g. `docqa`) your user can access
- An **[OpenAI API key](https://platform.openai.com/api-keys)**

## First-time setup

1. Create the database and enable pgvector (example — adjust user/host as needed):

   ```sql
   CREATE DATABASE docqa;
   \c docqa
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

2. Copy and edit environment:

   ```bash
   cp .env.example .env
   ```

   Set `OPENAI_API_KEY`, the `OPENAI_*` model variables (see `.env.example`), and optionally `DATABASE_URL`. If unset, the API defaults to:

   `postgresql+asyncpg://postgres:postgres@localhost:5432/docqa`

3. Install dependencies (root tool + frontend + Python packages):

   ```bash
   npm run setup
   ```

## Start the app (single command)

From the **repository root**:

```bash
npm start
```

This runs the FastAPI backend on [http://127.0.0.1:8000](http://127.0.0.1:8000) and the Vite frontend on [http://localhost:5173](http://localhost:5173) (with `/api` proxied to the backend). Press `Ctrl+C` once to stop both.

- API: `GET http://127.0.0.1:8000/api/health`, `POST /api/documents`, `POST /api/chat`

## Architecture

- **Frontend**: Vite + React; dev server proxies `/api` to the API.
- **Backend**: FastAPI + async SQLAlchemy + pgvector.

Required env for the API: `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_DIMENSIONS`. Examples are in `.env.example`.

## Ephemeral chat

There is **no** `messages` table and **no** `localStorage` / `sessionStorage` for chat. Only React state holds the thread; a full page reload starts over.
