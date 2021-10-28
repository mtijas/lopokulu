# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from manager.models import Vehicle

def validate_positive(value):
    if value <= 0:
        raise ValidationError(_('Value should be over zero'))


class Fillup(models.Model):
    price = models.DecimalField(
        "Price per unit", decimal_places=3, max_digits=5, validators=[validate_positive])
    amount = models.FloatField("Total filled up amount", validators=[validate_positive])
    distance = models.FloatField("Total odometer")

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'({self.vehicle}) {self.distance}, {self.amount} @ {self.price}'
