import os
import json
import hashlib
from typing import List, Optional, Dict, Any

# Defer importing httpx until we actually need network calls so MOCK_LLM
# can be used without installing httpx.

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
# Development/testing: when true, LLMService returns deterministic mock responses
MOCK_LLM = os.environ.get("MOCK_LLM", "false").lower() in ("1", "true", "yes")


class LLMService:
    """Minimal async wrapper for OpenAI embeddings + chat completions.

    This is intentionally simple for an MVP. It uses the OpenAI REST API
    via `httpx.AsyncClient`. Replace or extend this class to add other
    providers or a local adapter.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self._client = None

    async def _client(self):
        import httpx
        return httpx.AsyncClient(timeout=30.0, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })

    async def embed_text(self, text: str) -> Optional[List[float]]:
        """Return embedding vector for given text using OpenAI embeddings API."""
        # Mock mode: return a deterministic pseudo-embedding (small vector)
        if MOCK_LLM:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            # Convert bytes -> list of floats in range [-1,1]
            vec = [((b % 128) / 64.0) - 1.0 for b in digest[:32]]
            return vec

        if not self.api_key:
            return None

        url = "https://api.openai.com/v1/embeddings"
        payload = {"model": EMBEDDING_MODEL, "input": text}

        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            if r.status_code != 200:
                return None
            data = r.json()
            emb = data.get("data", [])[0].get("embedding") if data.get("data") else None
            return emb

    async def summarize(self, text: str, contexts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Produce a concise summary + key findings given a primary text and optional contexts.

        Returns structured JSON: {summary: str, key_findings: [str], used_contexts: [id_or_text]}
        """
        # Mock-mode: return a short deterministic summary without calling OpenAI
        if MOCK_LLM:
            summary = (
                text.strip().replace("\n", " ")[:600] + "..."
                if len(text.strip()) > 120 else text.strip()
            )
            findings = [
                "Main finding: " + (summary.split('.')[0] if summary else "none"),
                "Evidence: derived from provided abstract(s).",
                "Recommendation: review primary sources and clinical context."
            ]
            used = contexts[:3] if contexts else []
            return {"summary": summary, "key_findings": findings, "used_contexts": used}

        if not self.api_key:
            return {"summary": "", "key_findings": [], "used_contexts": []}

        system_prompt = (
            "You are an expert biomedical research summarization assistant. "
            "Given an abstract and supporting evidence, produce a concise summary of key findings, "
            "3-6 bullet points of evidence, and list citations as provenance (PMID or title).")

        # Build the user prompt
        prompt_parts = [f"Primary Abstract:\n{text}"]
        if contexts:
            prompt_parts.append("Supporting abstracts:\n" + "\n---\n".join(contexts[:6]))

        prompt_parts.append(
            "Produce: (1) `summary` (3-5 sentences), (2) `key_findings` list (3 bullets), (3) `provenance` list. "
            "Return JSON only."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "\n\n".join(prompt_parts)},
        ]

        url = "https://api.openai.com/v1/chat/completions"
        payload = {
            "model": LLM_MODEL,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": 600,
        }

        import httpx
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            if r.status_code != 200:
                return {"summary": "", "key_findings": [], "used_contexts": []}
            data = r.json()
            # Extract text
            text_out = ""
            try:
                text_out = data["choices"][0]["message"]["content"]
            except Exception:
                text_out = data.get("choices", [])[0].get("text", "")

            # Try to parse JSON from assistant output
            try:
                parsed = json.loads(text_out)
                return parsed
            except Exception:
                # If not JSON, return raw text in summary field
                return {"summary": text_out, "key_findings": [], "used_contexts": []}

    async def generate_report(self, title: str, prediction: Dict[str, Any], evidence_texts: List[str]) -> Dict[str, Any]:
        """Generate a full narrative report combining prediction and evidence.

        Returns a small JSON with `report_text` and optional `attachments`.
        """
        # Mock-mode: stitch together a short report from inputs
        if MOCK_LLM:
            header = f"{title}\n\nExecutive summary:\n"
            exec_sum = "This report summarizes model predictions and supporting evidence."
            evidence_snippets = "\n\n".join([e.strip()[:400] for e in evidence_texts[:6]])
            rec = "\n\nRecommendations:\n- Validate prediction with experimental data.\n- Consult clinical experts before interpretation."
            report = header + exec_sum + "\n\nEvidence:\n" + evidence_snippets + rec
            return {"report_text": report}

        prompt = (
            f"Report title: {title}\n\nPrediction:\n{json.dumps(prediction, indent=2)}\n\nEvidence:\n"
            + "\n---\n".join(evidence_texts[:8])
            + "\n\nWrite a concise professional report (600-1200 words) with an executive summary, key evidence, and recommendations."
        )

        url = "https://api.openai.com/v1/chat/completions"
        payload = {"model": LLM_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 1500}

        import httpx
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, json=payload)
            if r.status_code != 200:
                return {"report_text": ""}
            data = r.json()
            report_text = data["choices"][0]["message"]["content"] if data.get("choices") else ""
            return {"report_text": report_text}


# Singleton instance for convenience
llm_service = LLMService()
