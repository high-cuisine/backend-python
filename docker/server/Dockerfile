FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /cocktails
COPY ./cocktails/requirements.txt /cocktails/requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY ./cocktails /cocktails

EXPOSE 8000
EXPOSE 8089

COPY ./docker/server/entrypoint.sh /
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
