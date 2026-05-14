# Document Q&A (OpenAI, in-memory index)

Full-stack RAG app: upload `.txt`, `.pdf`, or `.docx`, ask questions grounded in that document. **Chat is only kept in browser memory** — refresh clears messages and the selected document. **Uploaded chunks and embeddings live in the API process memory** — restarting the backend clears them; there is no database.

## Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.12+ on your `PATH` (use a venv if you prefer; the `api` script uses `python`)
- An **[OpenAI API key](https://platform.openai.com/api-keys)**

## First-time setup

1. Copy and edit environment:

   ```bash
   cp .env.example .env
   ```

   Set `OPENAI_API_KEY` and the `OPENAI_*` model variables (see `.env.example`).

2. Install dependencies:

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
- **Backend**: FastAPI; document chunks and embedding vectors are stored in a **process-local in-memory store** with cosine-similarity retrieval (no Postgres).

Required env for the API: `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`, `OPENAI_EMBEDDING_DIMENSIONS`. Examples are in `.env.example`.

## Ephemeral data

There is **no** persisted chat and **no** database for documents. Browser refresh clears the UI session; **restarting the API** clears all uploaded documents and vectors.
