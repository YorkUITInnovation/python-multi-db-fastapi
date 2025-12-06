.PHONY: help build up down restart logs shell clean test health

# Default target
help:
	@echo "YorkU Multi-DB API - Docker Commands"
	@echo "====================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev-build    - Build development image"
	@echo "  make dev-up       - Start development container (with hot-reload)"
	@echo "  make dev-down     - Stop development container"
	@echo "  make dev-logs     - View development logs"
	@echo ""
	@echo "Production:"
	@echo "  make build        - Build production image"
	@echo "  make up           - Start production container"
	@echo "  make down         - Stop production container"
	@echo "  make restart      - Restart production container"
	@echo "  make logs         - View production logs"
	@echo ""
	@echo "Utilities:"
	@echo "  make shell        - Open shell in running container"
	@echo "  make health       - Check container health"
	@echo "  make clean        - Remove all containers and images"
	@echo "  make test         - Run tests inside container"
	@echo ""

# Production commands
build:
	docker compose -f docker-compose.prod.yml build

up:
	docker compose -f docker-compose.prod.yml up -d

down:
	docker compose -f docker-compose.prod.yml down

restart:
	docker compose -f docker-compose.prod.yml restart

logs:
	docker compose -f docker-compose.prod.yml logs -f

# Development commands
dev-build:
	docker compose -f docker-compose.dev.yml build

dev-up:
	docker compose -f docker-compose.dev.yml up -d
	@echo "Development server running at http://localhost:8082"
	@echo "API docs available at http://localhost:8082/docs"

dev-down:
	docker compose -f docker-compose.dev.yml down

dev-logs:
	docker compose -f docker-compose.dev.yml logs -f

# Utility commands
shell:
	@if [ -f docker-compose.dev.yml ] && docker compose -f docker-compose.dev.yml ps | grep -q "Up"; then \
		docker compose -f docker-compose.dev.yml exec api bash; \
	else \
		docker compose -f docker-compose.prod.yml exec api bash; \
	fi

health:
	@echo "Checking container health..."
	@curl -s http://localhost:8082/health | python -m json.tool || echo "Container not responding"

clean:
	docker compose -f docker-compose.prod.yml down -v
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f

test:
	@if [ -f docker-compose.dev.yml ] && docker compose -f docker-compose.dev.yml ps | grep -q "Up"; then \
		docker compose -f docker-compose.dev.yml exec api pytest; \
	else \
		docker compose -f docker-compose.prod.yml exec api pytest; \
	fi

# Quick rebuild (production)
rebuild: down build up
	@echo "Production container rebuilt and started"

# Quick rebuild (development)
dev-rebuild: dev-down dev-build dev-up
	@echo "Development container rebuilt and started"

