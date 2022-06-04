# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models import Equipment, EquipmentUser

admin.site.register(Equipment)
admin.site.register(EquipmentUser)
