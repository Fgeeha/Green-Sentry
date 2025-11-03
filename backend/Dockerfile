FROM python:3.12-slim as builder

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1 \
    libglx0 \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install poetry==2.2.1

# Конфигурация Poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

# Копирование файлов зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей
RUN poetry install --no-root --without dev && rm -rf $POETRY_CACHE_DIR

# Финальный образ
FROM python:3.12-slim as runtime

# Установка runtime зависимостей
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libxrender1 \
    libgomp1 \
    libgl1 \
    libglx0 \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование виртуального окружения
COPY --from=builder /app/.venv /app/.venv

# Копирование кода приложения
COPY app ./app
COPY data ./data

# Настройка PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Создание директорий
RUN mkdir -p /app/uploads /app/logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]