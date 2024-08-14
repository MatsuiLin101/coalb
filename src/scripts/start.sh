#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset
set -o xtrace

python manage.py migrate
# python manage.py compilemessages
python manage.py collectstatic --noinput

# python manage.py runserver 0.0.0.0:80
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --reload
