# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.apps import AppConfig


class FillupConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fillup"
