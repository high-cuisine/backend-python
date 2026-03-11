FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /cocktails
COPY ./cocktails/requirements.txt /cocktails/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY ./cocktails /cocktails