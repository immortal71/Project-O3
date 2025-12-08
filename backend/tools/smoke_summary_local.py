"""Local smoke test that calls the LLMService directly in MOCK mode.
Run:
  python backend/tools/smoke_summary_local.py
This will set MOCK_LLM=true before importing the module to force offline behavior.
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Ensure mock mode before importing the service
os.environ.setdefault("MOCK_LLM", "true")

# Add project root to sys.path so `import backend` works regardless of CWD
root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from backend.services.llm_service import llm_service

async def main():
    text = (
        "This is a sample abstract: A new oncology compound demonstrates tumor growth inhibition in preclinical models. "
        "Mechanism: pathway X inhibition leading to apoptosis in cell lines."
    )
    contexts = [
        "Supporting evidence A: in vitro studies show pathway modulation.",
        "Supporting evidence B: toxicology signals at high doses in rodents."
    ]

    result = await llm_service.summarize(text, contexts)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    asyncio.run(main())
