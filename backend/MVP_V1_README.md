# OncoPurpose — MVP v1 Readme

This document summarizes the v1 (ETA) scope and how to run the backend locally for testing.

Scope for MVP v1
- Prediction: Use `backend/predictor.py` to produce confidence scores and store results in `drug_cancer_predictions`.
- Evidence retrieval: Use PubMed/DrugBank connectors to ingest metadata into `research_papers` and associated tables.
- Summarization: Provide an LLM-based summary endpoint for papers (`/api/v1/research/papers/{id}/summary`).
- Background jobs: `sync_jobs.py` contains job implementations; wire to Celery later.

Files added in this work
- `backend/services/llm_service.py` — OpenAI wrapper for embeddings + chat completions.
- `backend/services/vector_store.py` — in-memory vector store for retrieval.
- `backend/research_api.py` — summary endpoint.
- `backend/LLM_INTEGRATION.md` — design doc for LLM integration.

Environment variables (minimum for MVP)
- `DATABASE_URL` — Async SQLAlchemy URL, e.g. `postgresql+asyncpg://postgres:pass@localhost:5432/oncopurpose`
- `REDIS_URL` — e.g. `redis://localhost:6379/0`
- `JWT_SECRET` — secret for signing JWTs
- `OPENAI_API_KEY` — required to use LLM summarization

Run locally (PowerShell)
```powershell
cd 'c:\Users\HUAWEI\Downloads\Project_O3\backend'
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Set example env vars (PowerShell)
$env:DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/oncopurpose"
$env:REDIS_URL = "redis://localhost:6379/0"
$env:OPENAI_API_KEY = "your_key_here"

# Run dev server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Quick smoke tests
- Health: `GET /health`
- Docs (development only): `/docs`
- Summarize a paper (example): `GET /api/v1/research/papers/{paper_id}/summary`

Next recommended steps
- Replace `InMemoryVectorStore` with `pgvector` or `FAISS` for reliable retrieval.
- Add Alembic migrations and a `Dockerfile` + `docker-compose.yml` for local development.
- Wire `sync_jobs.py` to Celery and add a worker Docker service.

Security note
- Never paste API keys or other secrets into chat or public places. Set secrets in environment variables or a secrets manager. The `OPENAI_API_KEY` must be set on your machine before running the summarization endpoint; do not send it to me.

Quick smoke-test script
1. Start the backend as above.
2. Set the env var in PowerShell (example):

```powershell
$env:OPENAI_API_KEY = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# then run the test
python tools\smoke_summary.py --paper-id <some-paper-uuid>
```

The test will call `GET /api/v1/research/papers/{id}/summary` and print the JSON response.
