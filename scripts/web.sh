#!/usr/bin/env bash

python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --config config/gunicorn.py --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:$PORT --timeout 300 --log-file -
