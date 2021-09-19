#!/bin/sh

python manage.py collectstatic --noinput
python manage.py migrate
python manage.py makemigrations
python manage.py migrate --fake
python manage.py create_users

exec "$@"