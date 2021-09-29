# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.db import models
from .vehicles import Vehicle


class Fillup(models.Model):
    price = models.DecimalField(
        "Price per unit", decimal_places=3, max_digits=5)
    amount = models.FloatField("Total filled up amount")
    distance = models.FloatField("Total odometer")

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.distance}, {self.amount} @ {self.price}'
