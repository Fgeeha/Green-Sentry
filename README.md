# 🌱 Green Sentry Pipeline

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12+-green)

Интеллектуальная система диагностики заболеваний растений с reasoning-компонентом на базе GigaChat и компьютерного зрения.

## ✨ Особенности

- 🤖 **CV + Reasoning**: Комбинация ResNet50 и GigaChat для точной диагностики
- 🎯 **Высокая точность**: 87%+ уверенность классификации
- 🌍 **Региональная адаптация**: Учет климата и географии
- 📊 **Детальный анализ**: Стадия заболевания, прогноз, план лечения
- 🔐 **Enterprise Security**: JWT, RBAC, Rate Limiting
- 📈 **Мониторинг**: Prometheus + Grafana
- 🚀 **Production Ready**: Docker, CI/CD, Автоскейлинг

## 🏗️ Архитектура

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│  React   │───▶│  Nginx   │───▶│ FastAPI  │
│ Frontend │    │  Proxy   │    │ Backend  │
└──────────┘    └──────────┘    └────┬─────┘
                                     │
                    ┌────────────────┼────────────┐
                    ▼                ▼            ▼
              ┌──────────┐    ┌─────────┐   ┌────────┐
              │PostgreSQL│    │  Redis  │   │ Celery │
              └──────────┘    └─────────┘   └────────┘
```

## 🚀 Быстрый старт

### Требования

- Docker & Docker Compose
- Python 3.10+ (для локальной разработки)
- Node.js 18+ (для локальной разработки)
- GigaChat API Key

### Установка

```bash
# 1. Клонирование
git clone https://github.com/fgeeha/Green-Sentry.git
cd plant-disease-reasoning

# 2. Конфигурация
cp .env.example .env
nano .env  # Добавьте GIGACHAT_API_KEY

# 3. Запуск
make install
make setup-db
make seed
make up

# 4. Открыть
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Grafana: http://localhost:3001
```

## 📖 Документация

- [API Documentation](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Contributing Guide](docs/CONTRIBUTING.md)

## 🛠️ Makefile команды

```bash
# Разработка
make dev              # Запустить полный стек
make dev-backend      # Только backend
make dev-frontend     # Только frontend

# Тестирование
make test             # Все тесты
make test-unit        # Unit тесты
make coverage         # Покрытие кода

# Качество кода
make lint             # Линтеры
make format           # Форматирование
make security         # Проверка безопасности

# База данных
make migrate          # Создать миграцию
make migrate-up       # Применить миграции
make backup-db        # Бэкап БД

# Production
make prod-build       # Сборка prod образов
make prod-up          # Запуск prod

# Утилиты
make logs             # Логи всех сервисов
make health           # Проверка здоровья
make clean            # Очистка
```

## 📊 Тестирование

```bash
# Запуск всех тестов
make test

# Запуск с покрытием
make coverage

# Только unit тесты
make test-unit

# Только integration тесты
make test-integration
```

## 🔒 Безопасность

- ✅ JWT Authentication
- ✅ Password hashing (bcrypt)
- ✅ RBAC (Role-Based Access Control)
- ✅ Rate Limiting
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ XSS protection
- ✅ CORS configuration

## 📈 Performance

- ⚡ Redis caching
- ⚡ Async operations
- ⚡ Connection pooling
- ⚡ Image optimization
- ⚡ Lazy loading
- ⚡ Celery для heavy tasks

## 🌟 Основные технологии

### Backend
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PyTorch** - ML framework
- **GigaChat** - Reasoning AI
- **Celery** - Task queue
- **Redis** - Cache & broker
- **PostgreSQL** - Database

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Dropzone** - File upload

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Nginx** - Reverse proxy
- **GitHub Actions** - CI/CD
- **Prometheus** - Metrics
- **Grafana** - Dashboards

