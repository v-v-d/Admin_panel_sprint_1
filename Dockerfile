FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1

COPY requirements/*.txt ./

RUN pip3 install --upgrade pip \
    && pip3 install -r prod.txt

ADD movies_admin /app
ADD entrypoint.sh /entrypoint.sh
RUN chmod a+x /entrypoint.sh

WORKDIR /app

ENV PYTHONPATH=/app

ENTRYPOINT ["/entrypoint.sh"]

CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000
