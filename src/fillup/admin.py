# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib import admin

from .models.fillups import Fillup
from .models.vehicles import Vehicle
from .models.vehicles_users import VehicleUser

admin.site.register(Fillup)
admin.site.register(Vehicle)
admin.site.register(VehicleUser)
