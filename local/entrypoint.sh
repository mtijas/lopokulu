#!/bin/sh

sleep 5
python3 /src/manage.py makemigrations --no-input
python3 /src/manage.py migrate
python3 /src/manage.py runserver 0.0.0.0:8000
