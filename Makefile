.PHONY: help up down logs run worker test coverage migrate makemigrations lint clean

#Show command options
help:
	@echo " CineReserve API Commands"
	@echo ""
	@echo " Infrastructure (Docker):"
	@echo "  make up          - Start all containers (API, DB, Redis, Celery)"
	@echo "  make down        - Stop containers and network"
	@echo "  make logs        - Show Docker logs"
	@echo ""
	@echo " Local Development (Poetry):"
	@echo "  make run         - Start the local Django server"
	@echo "  make worker      - Start the Celery Worker (for debugging emails)"
	@echo ""
	@echo " Test Suite:"
	@echo "  make test        - Run tests with pytest"
	@echo "  make coverage    - Run tests and generate coverage report"
	@echo ""
	@echo "  Database:"
	@echo "  make makemigrations - Create new migrations based on models"
	@echo "  make migrate     - Apply migrations to the database (PostgreSQL)"
	@echo ""
	@echo " Code Quality:"
	@echo "  make lint        - Run Ruff (Supersonic linter in Rust)"
	@echo "  make clean       - Remove temporary cache files (.pyc, pytest_cache)"

#Docker commands
up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

#Local commands
run:
	poetry run python manage.py runserver

worker:
	poetry run celery -A config worker -l info

#Tests
test:
	poetry run pytest tests/ -v

coverage:
	poetry run pytest tests/ --cov=apps --cov-report=term-missing

#Database
makemigrations:
	poetry run python manage.py makemigrations

migrate:
	poetry run python manage.py migrate

#Code quality (Linter)
lint:
	poetry run ruff check .

#Clear cache
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache
