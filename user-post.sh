#!/usr/bin/env bash

echo "Running post build script"
pip install -r requirements.txt
npm ci

python manage.py collectstatic --noinput
