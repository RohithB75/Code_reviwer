# AI Code Reviewer

Industry-grade AI Code Reviewer scaffold built with a FastAPI backend and a Streamlit frontend. This README covers local development, Docker, testing, and production guidance.

## Quick Start (Local)

1. Create and activate a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

3. Copy environment template and edit values:

```powershell
Copy-Item .env.example .env
```

4. Run services locally (development):

Backend (FastAPI):

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Frontend (Streamlit):

```powershell
cd frontend
streamlit run app.py --server.port 8501
```

The API default host/port when using Docker Compose is mapped to host port `8001` → container `8000` for convenience.

## Docker (Development)

Build and start both services with Compose (dev-friendly mounts and healthchecks):

```powershell
docker compose up --build
```

Notes:
- `.env` is mounted into the backend service so Pydantic `env_file` settings can read it inside the container.
- `CORS_ORIGINS` should be a JSON array string in `.env`, e.g.:

```
CORS_ORIGINS=["http://localhost:3000","http://localhost:8501"]
```

## Tests

Run backend tests with pytest:

```powershell
cd backend
pytest -q
```

There is a unit test validating the `ReportEngine` assembly and export metadata.

## Configuration / Environment Variables

Required or commonly used variables (set in `.env` for dev or via your secrets manager in prod):
- `OPENAI_API_KEY` — API key for LLM provider (if used)
- `MODEL_NAME` — LLM model identifier
- `BACKEND_BASE_URL` — e.g., `http://localhost:8001`
- `CORS_ORIGINS` — JSON array or comma-separated string; e.g. `["http://localhost:3000","http://localhost:8501"]`
- `LOG_FILE` — optional file path to enable rotating file logging inside the backend container

The application now tolerates both JSON arrays and comma-separated values for `CORS_ORIGINS` to avoid startup failures from env formatting.

## Production Recommendations

- Use a production process manager (Gunicorn with Uvicorn workers) instead of the development `--reload` server.
- Build a production Docker image (multi-stage) that excludes source mounts and development tools.
- Add CI (GitHub Actions) to run tests, lint (ruff/flake8), and format (black) on each PR.
- Add automated integration tests that mock LLM responses for stable CI runs.
- Add monitoring and error tracking (Prometheus/OpenTelemetry + Sentry) for observability.

## What changed recently

- Added support for combined report export metadata (JSON + Markdown) and ensured `markdown_report` is preserved for PDF export.
- Hardened environment parsing for `CORS_ORIGINS` and added optional rotating file logging via `LOG_FILE`.
- Added a pytest for the `ReportEngine` and Docker Compose configuration improvements.

## Next steps / Roadmap

- Create a production-ready `Dockerfile` and `docker-compose.prod.yml` with Gunicorn + Uvicorn workers.
- Expand unit and integration tests and add CI.
- Improve structured logging, tracing, and metrics.

---

If you'd like, I can add a `docker-compose.prod.yml`, production `Dockerfile`, and a GitHub Actions CI workflow next. 
