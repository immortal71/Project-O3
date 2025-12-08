# OncoPurpose Backend - Quick Start

[![License: All Rights Reserved](https://img.shields.io/badge/license-All%20Rights%20Reserved-lightgrey)](../LICENSE)

This README provides quick local development steps to run the FastAPI backend.

Prerequisites
- Python 3.11+
- PostgreSQL (for full functionality) or sqlite for quick tests
- Redis (for rate limiting and refresh token store)

Setup (PowerShell)
```powershell
Set-Location 'C:\Users\HUAWEI\Downloads\Project_O3\backend'

# Create and activate virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Copy example .env and set required env vars (SECRET_KEY, DATABASE_URL, REDIS_URL)
copy .env.example .env
notepad .env

# Run database migrations or initialize DB (if using PostgreSQL)
# alembic upgrade head

# Run development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Notes
- The repository contains a local `app/` import shim that maps `app.*` imports to the
  existing `backend/` package. This is for convenience in local development and is
  non-destructive.
- Refresh tokens are stored in Redis for revocation and rotation. Ensure `REDIS_URL`
  is set in `.env` before running the server.
# OncoPurpose Backend - Quick Start

This README contains quick local development steps for the backend API.

Prerequisites
- Python 3.11+
- PostgreSQL (for full integration) — not required for basic import checks
- Redis (for rate limiting and token storage)

Local setup (PowerShell)

```powershell
# Change to backend directory
Set-Location 'C:\Users\HUAWEI\Downloads\Project_O3\backend'

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create a .env file with required settings (see config.py for keys)
# Example minimal .env:
# SECRET_KEY=replace_with_secure_random_value
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/oncopurpose
# REDIS_URL=redis://localhost:6379/0

# Run the app (development)
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Notes
- The repository includes an `app/` import shim so imports like `app.core.config`
  resolve to the existing `backend/` modules for local development without moving files.
- For production, run behind a reverse proxy (nginx) and use real secrets management.

## License

This backend is distributed under a proprietary license (All Rights Reserved).
Please see the top-level `LICENSE` file for details, or contact the author for
licensing options and permissions: `oncopurpose@trovesx.com`.

If you'd rather use a standard open-source license for this repository (for
example, MIT, Apache 2.0, or GPLv3), please contact the author to discuss.
