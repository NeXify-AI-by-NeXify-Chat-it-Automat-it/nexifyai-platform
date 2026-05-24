.PHONY: help install dev test lint clean run run-dev docker-build docker-up

help: ## Zeige diese Hilfe
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installiere Produktions-Dependencies
	uv pip install -e ".[prod]" || pip install -e ".[prod]"

install-dev: ## Installiere alle Dev-Dependencies
	uv pip install -e ".[dev,prod]" || pip install -e ".[dev,prod]"

dev: ## Starte Development Server mit Hot-Reload
	cd services/api && uvicorn server:app --reload --host 0.0.0.0 --port 8000

run: ## Starte Production Server
	cd services/api && uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4

test: ## Führe Tests aus
	cd services/api && python -m pytest $(filter-out $@,$(MAKECMDGOALS))

lint: ## Lint-Check mit ruff
	ruff check services/api/ --fix
	ruff format services/api/ --check

format: ## Formatiere mit ruff
	ruff format services/api/

type-check: ## Type-Check mit mypy
	mypy services/api/

clean: ## Cleanup Python-Cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache .ruff_cache .mypy_cache .langchain_cache

docker-build: ## Docker-Build
	docker compose -f infrastructure/docker/docker-compose.yml build

docker-up: ## Docker-Start
	docker compose -f infrastructure/docker/docker-compose.yml up -d

docker-down: ## Docker-Stop
	docker compose -f infrastructure/docker/docker-compose.yml down

# Allow args for test
%:
	@:
