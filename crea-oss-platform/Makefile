.PHONY: help install dev-setup up down logs test clean

help:
	@echo "CREA OSS Platform - Makefile"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make dev-setup    - Setup development environment"
	@echo "  make up           - Start Docker services"
	@echo "  make down         - Stop Docker services"
	@echo "  make logs         - View Docker logs"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean temporary files"

install:
	cd backend && pip install -r requirements.txt

dev-setup:
	cd backend && cp .env.example .env
	@echo "Edit backend/.env with your configuration"

up:
	cd infra && docker-compose up -d

down:
	cd infra && docker-compose down

logs:
	cd infra && docker-compose logs -f

test:
	cd backend && pytest

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
