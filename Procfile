web: python defend_data_capture/manage.py migrate --noinput && gunicorn --chdir ./defend_data_capture defend_data_capture.wsgi:application --bind 0.0.0.0:$PORT --log-file -