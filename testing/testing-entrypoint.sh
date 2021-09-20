#!/bin/sh

python3 /app/manage.py collectstatic
gunicorn lopokulu.wsgi:application --bind 0.0.0.0:8000
