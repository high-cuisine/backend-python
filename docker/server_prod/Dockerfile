FROM python:3.11-alpine as builder

RUN apk update && \
    apk add --no-cache build-base postgresql-dev gcc python3-dev musl-dev openssl libffi-dev openssl-dev py3-pip

ARG TEMP_PATH=/usr/src/web

COPY ./cocktails/requirements.txt $TEMP_PATH/requirements.txt

RUN pip install --upgrade pip setuptools && \
    pip install --no-warn-script-location --prefix=/install -r $TEMP_PATH/requirements.txt


FROM python:3.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Europe/Moscow \
    LANG=C.UTF-8 \
    APP_HOME=/cocktails

ARG GID=1000
ARG UID=1000
ARG USER=ubuntu

RUN apk update && \
    apk add --no-cache postgresql-dev curl && \
    addgroup -g $GID -S $USER && \
    adduser -S $USER -G $USER --disabled-password --uid "$UID" && \
    mkdir -p /gunicorn_socket /redis_socket && \
    chmod -R 777 /gunicorn_socket /redis_socket && \
    chown -R $USER:$USER /gunicorn_socket

WORKDIR $APP_HOME

COPY --from=builder /install /usr/local
COPY --chown=$USER:$USER ./docker/server_prod/entrypoint.sh /
COPY --chown=$USER:$USER ./cocktails $APP_HOME

RUN chmod +x /entrypoint.sh && \
    mkdir -p static media  && \
    chown -R $USER:$USER $APP_HOME static media

USER $USER

EXPOSE 8000
