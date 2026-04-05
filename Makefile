.PHONY: install install-dev dev worker migrate migrate-new lint lint-fix \
        type-check test infra-up infra-down start-local start-json up down logs

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

infra-up:
	docker compose up -d postgres redis

infra-down:
	docker compose stop postgres redis

dev:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

worker:
	arq src.worker.WorkerSettings

start-local:
	uvicorn src.main:app --reload --host 127.0.0.1 --port 8000

start-json:
	STORAGE_BACKEND=json uvicorn src.main:app --reload --port 8000

migrate:
	alembic upgrade head

migrate-new:
	alembic revision --autogenerate -m "$(name)"

migrate-down:
	alembic downgrade -1

lint:
	ruff check src tests
	ruff format --check src tests

lint-fix:
	ruff check --fix src tests
	ruff format src tests

type-check:
	mypy src

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f app worker
