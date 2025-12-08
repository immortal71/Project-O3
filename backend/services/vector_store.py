"""A tiny in-memory vector store for MVP retrieval (no external dependencies).

This is intentionally lightweight: it stores id->(vector, metadata) in memory
and performs cosine-similarity searches with numpy. Replace with pgvector,
FAISS, or another vector DB for production.
"""
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class InMemoryVectorStore:
    def __init__(self):
        # id -> (vector, metadata)
        self._data: Dict[str, Tuple[np.ndarray, Dict[str, Any]]] = {}

    def upsert(self, id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        arr = np.array(vector, dtype=np.float32)
        # normalize for cosine similarity
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        self._data[id] = (arr, metadata or {})

    def query_similar(self, vector: List[float], k: int = 5) -> List[Dict[str, Any]]:
        if not self._data:
            return []
        q = np.array(vector, dtype=np.float32)
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        results = []
        for id, (vec, meta) in self._data.items():
            score = float(np.dot(q, vec))
            results.append({"id": id, "score": score, "metadata": meta})

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:k]


# Convenience singleton
GLOBAL_VECTOR_STORE = InMemoryVectorStore()
