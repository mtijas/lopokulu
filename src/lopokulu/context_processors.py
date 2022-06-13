# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.conf import settings


def measurement_apps(request):
    return {
        "MEASUREMENT_APPS": settings.INSTALLED_MEASUREMENT_APPS,
    }
