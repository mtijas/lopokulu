#!/bin/sh

python3 /app/manage.py makemigrations --no-input
python3 /app/manage.py migrate
python3 manage.py runserver 0.0.0.0:8000
