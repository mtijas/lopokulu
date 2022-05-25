# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from measurements.models import Measurement

admin.site.register(Measurement)
