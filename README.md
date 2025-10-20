# File Upload Sytem

A minimal full-stack example showcasing clean API design, async concurrency control, and frontend integration.

## Stack
**Backend**
- FastAPI
- In-memory file storage
- Concurrency limits, deduping, metrics, and typed models
- Pytest + Ruff + Mypy + Bandit checks

**Frontend**
- Next.js + React 18
- Type-safe API client via `openapi-typescript`
- File uploads with drag-drop, progress, and listing
- E2E tests with [Playwright](https://playwright.dev/)

---

## Local Development

### 1. Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cd ..
make api
```
Runs on **http://localhost:8000**

Docs available at:
- ReDoc: http://localhost:8000/redoc

### 2. Frontend
```bash
make web
```
Runs on **http://localhost:3000**

---

## Testing

### Unit + Integration
```bash
make test
```

### Linting + Type Checking
```bash
make lint
```

### Auto-fix Formatting
```bash
make fmt
```

---

## Code Generation
When the backend is running, regenerate frontend API types:
```bash
make generate
```

---

## Docker (optional)
Run the full stack via Docker Compose:
```bash
make dev
```
Rebuilds and serves both backend and frontend.

---

## Metrics & Health
- `/api/v1/health` → uptime
- `/api/v1/metrics` → runtime counters
- `/api/v1/files` → list uploaded files
- `/api/v1/upload` → upload endpoint (multipart/form-data)
