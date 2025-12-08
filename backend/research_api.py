"""API router for research paper summaries and evidence retrieval.

This file adds `GET /research/papers/{paper_id}/summary` which uses the
LLM service + a vector store to produce a concise summary and provenance.
"""

# Copyright (c) 2025 OncoPurpose (trovesx)
# All Rights Reserved.
# For licensing info, see LICENSE or contact oncopurpose@trovesx.com
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import get_any_authenticated_user, get_db
from app.models.research import ResearchPaper
from app.services.llm_service import llm_service
from app.services.vector_store import GLOBAL_VECTOR_STORE

router = APIRouter(prefix="/research", tags=["Research"])


@router.get("/papers/{paper_id}/summary")
async def get_paper_summary(
    paper_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_any_authenticated_user),
):
    """Return an LLM-generated summary for a research paper with provenance."""
    # Load paper
    result = await db.execute(select(ResearchPaper).where(ResearchPaper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paper not found")

    abstract = paper.abstract or ""
    if not abstract:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Paper has no abstract to summarize")

    # Ensure embedding exists in vector store and query neighbors
    emb = await llm_service.embed_text(abstract)
    neighbors: List[dict] = []
    if emb:
        # Upsert self (use paper id)
        GLOBAL_VECTOR_STORE.upsert(paper_id, emb, {"title": paper.title, "pubmed_id": paper.pubmed_id})
        neighbors = GLOBAL_VECTOR_STORE.query_similar(emb, k=6)

    # Build context texts from neighbors (skip self)
    contexts = []
    for n in neighbors:
        if n.get("id") == paper_id:
            continue
        # Load neighbor paper abstract if available from DB metadata; try to fetch from DB
        neighbor_id = n.get("id")
        try:
            r = await db.execute(select(ResearchPaper).where(ResearchPaper.id == neighbor_id))
            neighbor = r.scalar_one_or_none()
            if neighbor and neighbor.abstract:
                contexts.append(neighbor.abstract)
        except Exception:
            continue

    # Call LLM summarizer
    summary_obj = await llm_service.summarize(abstract, contexts)

    return {
        "paper_id": paper_id,
        "pubmed_id": paper.pubmed_id,
        "title": paper.title,
        "summary": summary_obj.get("summary"),
        "key_findings": summary_obj.get("key_findings"),
        "provenance": summary_obj.get("provenance") or [],
        "used_context_count": len(contexts),
    }
