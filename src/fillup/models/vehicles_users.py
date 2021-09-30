# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import models

from .vehicles import Vehicle


class VehicleUser(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Role(models.TextChoices):
        READ_ONLY = 'RO', _('Read only')
        DRIVER = 'DR', _('Driver')
        OWNER = 'OW', _('Owner')
    role = models.CharField(
        max_length=2, choices=Role.choices, default=Role.READ_ONLY)

    def __str__(self):
        return f'{self.vehicle.name} has {self.role} user {self.user}'
