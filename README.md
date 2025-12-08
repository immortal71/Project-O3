# Project O3 - OncoPurpose

This repository contains the OncoPurpose web application — AI-powered drug repurposing analysis platform for oncology.

## What's included
- Frontend static pages (Landing / Discovery / Library / Analytics)
- Backend (FastAPI) with OpenAI integration
- Data import tools (ChEMBL, PubChem, FDA) and sample data

## Quickstart (local dev)
1. Clone the repo
2. Setup Python virtualenv in `backend`:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and set environment variables (OPENAI_API_KEY, DATABASE_URL)

4. Run backend:

```powershell
uvicorn main_simple:app --reload --host 0.0.0.0 --port 8000
```

5. Open the frontend pages (static HTTP server) or open `index (1).html` directly to view the website.

## Notes
- The project includes `backend/.env.example`. Do not commit `.env` or secrets.
- Database files are intentionally excluded from the repository.
- License and attribution: ChEMBL requires attribution (CC-BY-SA), others are public domain.

## Contact
Project owner: immortal71 (GitHub)