# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from equipment.models import Equipment
from django.contrib.auth.models import User


class Measurement(models.Model):
    addition_date = models.DateTimeField(default=timezone.now)
    measurement = models.JSONField()
    measurement_type = models.CharField(max_length=64, default='BaseMeasurement')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    measurer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
