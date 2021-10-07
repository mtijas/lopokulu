# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models.fillups import Fillup
from .models.vehicles import Vehicle
from .models.vehicles_users import VehicleUser
from .models.persons import Person


class PersonInline(admin.StackedInline):
    model = Person
    can_delete = False
    verbose_name_plural = 'person'


class UserAdmin(BaseUserAdmin):
    inlines = (PersonInline,)


admin.site.register(Fillup)
admin.site.register(Vehicle)
admin.site.register(VehicleUser)
# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
