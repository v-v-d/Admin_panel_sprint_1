FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

COPY sqlite_to_postgres/requirements.txt .

RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt

ADD sqlite_to_postgres /app
ADD sqlite_to_postgres/settings /app/settings
WORKDIR /app

ENV PYTHONPATH=/app
