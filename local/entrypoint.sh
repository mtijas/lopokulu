#!/bin/sh

sleep 5
python3 /app/manage.py makemigrations --no-input
python3 /app/manage.py migrate
python3 /app/manage.py runserver 0.0.0.0:8000
