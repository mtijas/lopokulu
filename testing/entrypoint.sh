#!/bin/sh

sleep 5
python3 /app/manage.py collectstatic
gunicorn --chdir "/app" lopokulu.wsgi:application --bind 0.0.0.0:8000
