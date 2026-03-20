# syntax=docker/dockerfile:1

# =============================================================================
# ЭТАП 1: BUILDER - Сборка зависимостей
# =============================================================================
FROM python:3.11-slim-bookworm AS builder

# Переменные для кэширования и оптимизации
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    # Ограничиваем параллелизм компиляции для снижения потребления памяти
    MAKEFLAGS="-j2" \
    CFLAGS="-O2"

# Устанавливаем только необходимые зависимости для компиляции
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Рабочая директория
WORKDIR /usr/src/app

# Копируем только requirements.txt для лучшего кэширования слоев
COPY ./cocktails/requirements.txt .

# Кэширование pip и установка пакетов в отдельную директорию
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools wheel && \
    pip install --prefix=/install -r requirements.txt

# =============================================================================
# ЭТАП 2: RUNTIME - Минимальный образ для запуска
# =============================================================================
FROM python:3.11-slim-bookworm AS runtime

# Переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    TZ=Europe/Moscow \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    APP_HOME=/cocktails \
    # Оптимизация памяти для Python
    PYTHONMALLOC=malloc \
    # Gunicorn настройки
    GUNICORN_CMD_ARGS="--workers 2 --threads 2 --worker-class gthread --timeout 120 --keep-alive 5"

# Аргументы для пользователя
ARG GID=1000
ARG UID=1000
ARG USER=appuser

# Устанавливаем только рантайм зависимости (без компиляторов!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    libffi8 \
    libssl3 \
    libxml2 \
    libxslt1.1 \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    # Создаем пользователя с минимальными правами
    && addgroup --gid $GID --system $USER \
    && adduser --system --uid $UID --gid $GID $USER \
    # Создаем директории для сокетов
    && mkdir -p /gunicorn_socket /redis_socket \
    && chmod -R 777 /gunicorn_socket /redis_socket \
    && chown -R $USER:$USER /gunicorn_socket /redis_socket

# Рабочая директория
WORKDIR $APP_HOME

# Копируем установленные пакеты из builder
COPY --from=builder /install /usr/local

# Копируем скрипты и код приложения
COPY --chown=$USER:$USER ./docker/server_prod/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
COPY --chown=$USER:$USER ./cocktails $APP_HOME

#