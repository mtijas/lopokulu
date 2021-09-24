#!/bin/sh

sleep 5
python3 /src/manage.py collectstatic
gunicorn --chdir "/src" lopokulu.wsgi:application --bind 0.0.0.0:8000
