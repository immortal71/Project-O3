# LLM Integration (Option 1) — OncoPurpose

This document describes the simple LLM + retrieval integration used for the v1 MVP.

Overview
- Use the existing deterministic predictor (`backend/predictor.py`) for confidence scores.
- Use an LLM to generate readable summaries and reports from papers and retrieved evidence.
- Use embeddings to perform a lightweight retrieval (in-memory vector store for MVP).

Files added for Option 1
- `backend/services/llm_service.py` — small async OpenAI wrapper (embeddings + chat completions).
- `backend/services/vector_store.py` — `InMemoryVectorStore` for similarity search (replaceable with pgvector/FAISS).
- `backend/research_api.py` — new API router exposing `GET /api/v1/research/papers/{id}/summary`.

Environment variables
- `OPENAI_API_KEY` — required to use OpenAI for embeddings and chat completions.
- `EMBEDDING_MODEL` — optional overriding embedding model (default: `text-embedding-3-small`).
- `LLM_MODEL` — optional overriding LLM for chat (default: `gpt-4o-mini`).

How it works (MVP flow)
1. A request to `/api/v1/research/papers/{id}/summary` loads the paper abstract from the DB.
2. The backend obtains an embedding for the abstract with `llm_service.embed_text`.
3. The embedding is upserted into the `InMemoryVectorStore` and nearest neighbors are queried.
4. Neighbor abstracts are bundled with the primary abstract and sent to the LLM summarizer.
5. The LLM returns structured JSON (summary, key_findings, provenance). The endpoint returns that JSON and provenance metadata.

Notes & next steps
- The in-memory store is only suitable for development or small datasets. Replace with `pgvector`, `FAISS`, `Milvus`, or an external vector DB for production.
- The summarizer returns JSON when possible. It is advisable to validate/normalize outputs and log prompts/outputs for audit.
- For privacy-sensitive deployments, swap to a self-hosted model or use contract terms with a hosted provider.
