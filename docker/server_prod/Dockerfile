# syntax=docker/dockerfile:1
FROM python:3.11-slim-bookworm AS builder

# Устанавливаем только необходимые зависимости для компиляции
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

ARG TEMP_PATH=/usr/src/web
WORKDIR $TEMP_PATH

COPY ./cocktails/requirements.txt .

# Кэширование pip и установка пакетов
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip setuptools && \
    pip install --no-warn-script-location --prefix=/install -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow \
    LANG=C.UTF-8 \
    APP_HOME=/cocktails

ARG GID=1000
ARG UID=1000
ARG USER=ubuntu

# Устанавливаем рантайм зависимости (без компиляторов!)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --gid $GID --system $USER \
    && adduser --system --uid $UID --gid $GID $USER \
    && mkdir -p /gunicorn_socket /redis_socket \
    && chmod -R 777 /gunicorn_socket /redis_socket \
    && chown -R $USER:$USER /gunicorn_socket

WORKDIR $APP_HOME

# Копируем пакеты из builder
COPY --from=builder /install /usr/local

COPY --chown=$USER:$USER ./docker/server_prod/entrypoint.sh /
COPY --chown=$USER:$USER ./cocktails $APP_HOME

RUN chmod +x /entrypoint.sh && \
    mkdir -p static media && \
    chown -R $USER:$USER $APP_HOME static media

USER $USER

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]