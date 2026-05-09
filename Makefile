.PHONY: install install-dev dev worker cron-worker migrate migrate-new migrate-down \
        lint lint-fix type-check test start-json \
        dev-infra-up dev-infra-down up down logs

install:
	uv sync --active

install-dev:
	uv sync --active --extra dev

dev-infra-up:
	sudo docker compose -f docker-compose-dev.yml up -d --build

dev-infra-down:
	sudo docker compose -f docker-compose-dev.yml down

dev:
	cd src && uv run --active python -m uvicorn main:create_app --host=127.0.0.1 --port=8081 --reload

worker:
	cd src && uv run --active python ./domain_events_worker.py

cron-worker:
	cd src && uv run --active python ./cron_tasks_worker.py

start-json:
	cd src && STORAGE_BACKEND=json uv run --active python -m uvicorn main:create_app --host=127.0.0.1 --port=8081 --reload

migrate:
	cd src && uv run --active alembic upgrade head

migrate-new:
	cd src && uv run --active alembic revision --autogenerate -m "$(name)"

migrate-down:
	cd src && uv run --active alembic downgrade -1

lint:
	uv run --active ruff check src tests
	uv run --active ruff format --check src tests

lint-fix:
	uv run --active ruff check --fix src tests
	uv run --active ruff format src tests

type-check:
	uv run --active mypy src

test:
	uv run --active pytest tests/ -v --cov=src --cov-report=term-missing

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f app worker
