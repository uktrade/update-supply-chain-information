#!/usr/bin/env bash

echo "Running scripts/web.sh"

set -e

rootPath="$(dirname "$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )")"

cd "${rootPath}"
python --version

python manage.py migrate --noinput

python manage.py collectstatic --noinput

gunicorn config.wsgi:application --config config/gunicorn.py --worker-class gevent --worker-connections 1000 --bind 0.0.0.0:$PORT --timeout 300 --log-file -
