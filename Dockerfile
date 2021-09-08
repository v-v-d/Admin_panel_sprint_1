FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

COPY requirements/base.txt .
COPY requirements/dev.txt .

RUN pip3 install --upgrade pip \
    && pip3 install -r dev.txt

ADD movies_admin /app
WORKDIR /app

ENV PYTHONPATH=/app
