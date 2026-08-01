# AI Code Reviewer

Industry-grade AI Code Reviewer scaffold built with a FastAPI backend and a Streamlit frontend.

## Phase 1 Goals

- Production-ready project structure
- Clean architecture boundaries
- Docker-ready service layout
- Environment and dependency scaffolding
- No business logic yet

## Technology Stack

- Python 3.12
- FastAPI for the backend API
- Streamlit for the frontend experience
- Docker and Docker Compose for containerized runs

## Repository Layout

```text
.
├── backend/
├── frontend/
├── .env.example
├── .gitignore
├── .vscode/
└── docker-compose.yml
```

## Local Setup

1. Create a virtual environment with Python 3.12:

```powershell
py -3.12 -m venv .venv
```

2. Activate it:

```powershell
.venv\\Scripts\\Activate.ps1
```

3. Install backend dependencies:

```powershell
pip install -r backend/requirements.txt
```

4. Install frontend dependencies:

```powershell
pip install -r frontend/requirements.txt
```

5. Copy the environment template:

```powershell
Copy-Item .env.example .env
```

## Run Locally

Backend:

```powershell
cd backend
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
streamlit run app.py
```

## Docker

Build and start both services:

```powershell
docker compose up --build
```

## Tests

Run backend tests with pytest:

```powershell
cd backend
pytest -q
```

## Notes for Production

- Ensure environment variables are set (see `.env.example`).
- Use a process manager (Gunicorn + Uvicorn workers) for production backend instead of the development reloader and enable TLS termination at the proxy/load balancer.
- For frontend, build a static production artifact if using a web stack, or run Streamlit behind a reverse proxy with proper caching.

## Environment Variables

Populate the following values in `.env` when you are ready:

- `OPENAI_API_KEY`
- `MODEL_NAME`
- `BACKEND_BASE_URL`
- `CORS_ORIGINS`

## Placeholder Milestones

- Phase 2: backend domain and application use cases
- Phase 3: code analysis and review orchestration
- Phase 4: frontend review workflow and feedback views
- Phase 5: testing, observability, and deployment hardening
