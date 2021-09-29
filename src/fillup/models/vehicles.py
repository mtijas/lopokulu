# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.db import models


class Vehicle(models.Model):
    register_number = models.CharField("Register number", max_length=32)
    name = models.TextField("Name of the vehicle")

    def __str__(self):
        return f'({self.register_number}) {self.name}'
