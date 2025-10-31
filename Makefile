.PHONY: help install dev build up down logs test lint format clean migrate seed

# Цвета для вывода
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

DC = docker compose

help: ## Показать справку
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2}' $(MAKEFILE_LIST)

## ================== Установка и настройка ==================

install: ## Установить все зависимости
	@echo "${GREEN}Установка backend зависимостей...${RESET}"
	cd backend && poetry install
	@echo "${GREEN}Установка frontend зависимостей...${RESET}"
	cd frontend && npm install
	@echo "${GREEN}Копирование .env файла...${RESET}"
	cp -n .env.example .env || true
	@echo "${GREEN}✓ Установка завершена${RESET}"

setup-db: ## Создать базу данных и выполнить миграции
	@echo "${GREEN}Создание базы данных...${RESET}"
	cd backend && poetry run alembic upgrade head
	@echo "${GREEN}✓ База данных готова${RESET}"

seed: ## Заполнить БД тестовыми данными
	@echo "${GREEN}Заполнение базы данных...${RESET}"
	cd backend && poetry run python scripts/seed_db.py
	@echo "${GREEN}✓ Данные загружены${RESET}"

download-models: ## Скачать предобученные модели
	@echo "${GREEN}Загрузка моделей...${RESET}"
	cd backend && poetry run python scripts/download_models.py
	@echo "${GREEN}✓ Модели загружены${RESET}"

## ================== Разработка ==================

dev-backend: ## Запустить backend в режиме разработки
	cd backend && poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Запустить frontend в режиме разработки
	cd frontend && npm run dev

dev: ## Запустить полный стек для разработки
	@echo "${GREEN}Запуск в режиме разработки...${RESET}"
	${DC} up --build

## ================== Docker ==================

build: ## Собрать Docker образы
	@echo "${GREEN}Сборка Docker образов...${RESET}"
	${DC} build

up: ## Запустить все сервисы
	@echo "${GREEN}Запуск сервисов...${RESET}"
	${DC} up -d
	@echo "${GREEN}✓ Сервисы запущены${RESET}"
	@echo "${YELLOW}Frontend: http://localhost:3000${RESET}"
	@echo "${YELLOW}Backend: http://localhost:8000${RESET}"
	@echo "${YELLOW}API Docs: http://localhost:8000/docs${RESET}"

down: ## Остановить все сервисы
	@echo "${GREEN}Остановка сервисов...${RESET}"
	${DC} down
	@echo "${GREEN}✓ Сервисы остановлены${RESET}"

restart: down up ## Перезапустить все сервисы

logs: ## Показать логи всех сервисов
	${DC} logs -f

logs-backend: ## Показать логи backend
	${DC} logs -f backend

logs-frontend: ## Показать логи frontend
	${DC} logs -f frontend

ps: ## Показать статус контейнеров
	${DC} ps

## ================== Production ==================

prod-build: ## Собрать production образы
	@echo "${GREEN}Сборка production образов...${RESET}"
	${DC} -f docker-compose.prod.yml build

prod-up: ## Запустить production версию
	@echo "${GREEN}Запуск production...${RESET}"
	${DC} -f docker-compose.prod.yml up -d

prod-down: ## Остановить production
	${DC} -f docker-compose.prod.yml down

## ================== База данных ==================

migrate: ## Создать новую миграцию
	@read -p "Enter migration message: " msg; \
	cd backend && poetry run alembic revision --autogenerate -m "$$msg"

migrate-up: ## Применить миграции
	cd backend && poetry run alembic upgrade head

migrate-down: ## Откатить последнюю миграцию
	cd backend && poetry run alembic downgrade -1

migrate-history: ## Показать историю миграций
	cd backend && poetry run alembic history

db-reset: ## Сбросить базу данных (ОПАСНО!)
	@echo "${YELLOW}ВНИМАНИЕ: Это удалит все данные!${RESET}"
	@read -p "Продолжить? [y/N] " confirm; \
	if [ "$$confirm" = "y" ]; then \
		cd backend && poetry run alembic downgrade base && poetry run alembic upgrade head; \
		echo "${GREEN}✓ База данных сброшена${RESET}"; \
	fi

## ================== Тестирование ==================

test: ## Запустить все тесты
	@echo "${GREEN}Запуск тестов...${RESET}"
	cd backend && poetry run pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-unit: ## Запустить unit тесты
	cd backend && poetry run pytest tests/unit/ -v

test-integration: ## Запустить integration тесты
	cd backend && poetry run pytest tests/integration/ -v

test-e2e: ## Запустить e2e тесты
	cd backend && poetry run pytest tests/e2e/ -v

test-watch: ## Запустить тесты в watch режиме
	cd backend && poetry run ptw -- tests/ -v

coverage: ## Показать покрытие тестами
	cd backend && poetry run pytest tests/ --cov=app --cov-report=html
	@echo "${GREEN}Открытие отчета о покрытии...${RESET}"
	open backend/htmlcov/index.html || xdg-open backend/htmlcov/index.html

## ================== Качество кода ==================

lint: ## Проверить код линтерами
	@echo "${GREEN}Проверка backend...${RESET}"
	cd backend && poetry run ruff check app/
	cd backend && poetry run mypy app/
	@echo "${GREEN}Проверка frontend...${RESET}"
	cd frontend && npm run lint

format: ## Форматировать код
	@echo "${GREEN}Форматирование backend...${RESET}"
	cd backend && poetry run black app/ tests/
	cd backend && poetry run ruff check --fix app/
	@echo "${GREEN}Форматирование frontend...${RESET}"
	cd frontend && npm run format

format-check: ## Проверить форматирование
	cd backend && poetry run black --check app/ tests/

security: ## Проверить безопасность
	@echo "${GREEN}Проверка уязвимостей backend...${RESET}"
	cd backend && poetry run bandit -r app/
	@echo "${GREEN}Проверка уязвимостей frontend...${RESET}"
	cd frontend && npm audit

## ================== Бенчмарки и мониторинг ==================

benchmark: ## Запустить бенчмарки
	cd backend && poetry run python scripts/benchmark.py

load-test: ## Нагрузочное тестирование
	@echo "${GREEN}Запуск нагрузочного тестирования...${RESET}"
	docker run --rm -i grafana/k6 run --vus 10 --duration 30s - < tests/load/k6-script.js

monitor: ## Открыть мониторинг
	@echo "${GREEN}Открытие Grafana...${RESET}"
	open http://localhost:3001 || xdg-open http://localhost:3001

## ================== Очистка ==================

clean: ## Очистить временные файлы
	@echo "${GREEN}Очистка...${RESET}"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type d -name "node_modules" -prune -o -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "${GREEN}✓ Очистка завершена${RESET}"

clean-docker: ## Очистить Docker ресурсы
	@echo "${YELLOW}Очистка Docker...${RESET}"
	${DC} down -v --remove-orphans
	docker system prune -f

clean-all: clean clean-docker ## Полная очистка

## ================== Документация ==================

docs: ## Сгенерировать документацию
	@echo "${GREEN}Генерация документации...${RESET}"
	cd backend && poetry run pdoc --html --output-dir docs app

docs-serve: ## Запустить документацию локально
	cd backend && poetry run pdoc --http localhost:8080 app

## ================== CI/CD ==================

ci: lint test ## Запустить CI pipeline локально

pre-commit: format lint test ## Проверки перед коммитом

## ================== Утилиты ==================

shell-backend: ## Открыть shell в backend контейнере
	${DC} exec backend /bin/bash

shell-frontend: ## Открыть shell в frontend контейнере
	${DC} exec frontend /bin/sh

db-shell: ## Подключиться к базе данных
	${DC} exec postgres psql -U postgres -d plant_disease

backup-db: ## Создать бэкап базы данных
	@echo "${GREEN}Создание бэкапа...${RESET}"
	mkdir -p backups
	${DC} exec -T postgres pg_dump -U postgres plant_disease > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "${GREEN}✓ Бэкап создан в папке backups/${RESET}"

restore-db: ## Восстановить базу из бэкапа
	@echo "${YELLOW}Доступные бэкапы:${RESET}"
	@ls -1 backups/*.sql
	@read -p "Enter backup filename: " backup; \
	${DC} exec -T postgres psql -U postgres -d plant_disease < backups/$$backup

version: ## Показать версии
	@echo "${GREEN}Версии компонентов:${RESET}"
	@echo "Python: $$(cd backend && poetry run python --version)"
	@echo "Poetry: $$(poetry --version)"
	@echo "Node: $$(node --version)"
	@echo "npm: $$(npm --version)"
	@echo "Docker: $$(docker --version)"
	@echo "Docker Compose: $$(${DC} --version)"

health: ## Проверить здоровье сервисов
	@echo "${GREEN}Проверка backend...${RESET}"
	@curl -s http://localhost:8000/api/v1/health | jq . || echo "Backend недоступен"
	@echo "${GREEN}Проверка frontend...${RESET}"
	@curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3000 || echo "Frontend недоступен"

.DEFAULT_GOAL := help