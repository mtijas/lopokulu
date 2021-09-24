#!/bin/sh

# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: CC0-1.0

sleep 5
python3 /src/manage.py collectstatic --no-input
gunicorn --chdir "/src" lopokulu.wsgi:application --bind 0.0.0.0:8000
