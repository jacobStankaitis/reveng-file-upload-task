SHELL := /bin/bash
.ONESHELL:
.PHONY: dev api web test lint fmt generate ci

# default dev run with Docker Compose
dev:
	docker compose up --build

api:
	cd backend && source .venv/bin/activate &&	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd frontend && npm install && npm run dev

test:
	cd backend && pytest
	cd frontend && npm run test:e2e

lint:
	cd backend && ruff check . && mypy app
	cd backend && bandit -r app || true
	cd frontend && npm run lint

fmt:
	cd backend && ruff check . --fix
	cd frontend && npm run format

generate:
	./scripts/generate_api_types.sh

ci: lint test
