#!/bin/sh

# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: CC0-1.0

python3 /lopokulu/src/manage.py wait_for_database
python3 /lopokulu/src/manage.py makemigrations --no-input
python3 /lopokulu/src/manage.py migrate
gunicorn --chdir /lopokulu/src lopokulu.wsgi:application --bind 0.0.0.0:8000
