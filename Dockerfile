FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

COPY requirements/*.txt ./

RUN pip3 install --upgrade pip \
    && pip3 install -r prod.txt

ADD movies_admin /app
WORKDIR /app

ENV PYTHONPATH=/app

CMD python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && python manage.py makemigrations \
    && python manage.py migrate --fake \
    && python manage.py create_users \
    && python manage.py runserver 0.0.0.0:8000
