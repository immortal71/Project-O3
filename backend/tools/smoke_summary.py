"""Smoke test for the summarization endpoint.

Usage:
  python tools\smoke_summary.py --paper-id <paper_uuid> [--host http://127.0.0.1:8000]

This script reads `OPENAI_API_KEY` from the environment and performs a GET
request to the running backend summarization endpoint. It does NOT contain
any API key values — set the environment variable locally before running.
"""
import os
import argparse
import requests


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-id", required=True)
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    # Ensure OPENAI_API_KEY present locally
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not set in environment. The endpoint may still run in mock/unavailable mode.")

    url = f"{args.host}/api/v1/research/papers/{args.paper_id}/summary"
    print(f"Calling {url} ...")

    try:
        r = requests.get(url, timeout=60)
        print("Status:", r.status_code)
        print(r.text)
    except Exception as e:
        print("Request failed:", str(e))


if __name__ == "__main__":
    main()
