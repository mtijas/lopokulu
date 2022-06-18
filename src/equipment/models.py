# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Equipment(models.Model):
    name = models.CharField(max_length=256)
    register_number = models.CharField(max_length=256)
    # Needs 'list' instead of '[]' to get a fresh mutable object every time.
    # See https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield
    allowed_measurements = models.JSONField(default=list)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"({self.register_number}) {self.name}"


class EquipmentUser(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Role(models.TextChoices):
        READ_ONLY = "READ_ONLY", _("Read only")
        USER = "USER", _("User")
        ADMIN = "ADMIN", _("Administrator")

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.READ_ONLY)

    def __str__(self):
        return f"{self.equipment.name} has {self.role} user {self.user}"
