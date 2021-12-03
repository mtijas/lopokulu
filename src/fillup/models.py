# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from manager.models import Vehicle
from manager.models import Person
import decimal

def validate_positive(value):
    if value <= 0:
        raise ValidationError(_('Value should be over zero'))


class Fillup(models.Model):
    price = models.DecimalField(
        'Price per unit', decimal_places=3, max_digits=5, validators=[validate_positive])
    amount = models.FloatField('Total filled up amount', validators=[validate_positive])
    distance = models.FloatField('Total odometer')
    addition_date = models.DateTimeField(default=timezone.now)
    tank_full = models.BooleanField(default=True)
    distance_delta = models.FloatField(
        'Distance delta',
        null=True
    )
    total_price = models.FloatField(
        'Total price',
        null=True
    )
    consumption = models.FloatField(
        'Consumption',
        null=True
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    person = models.ForeignKey(
        Person,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def calculate_distance_delta(self):
        previous = Fillup.objects.filter(
            vehicle_id=self.vehicle.id,
            addition_date__lt=self.addition_date
        ).first()

        if previous is not None:
            return round(self.distance - previous.distance, 1)
        return self.distance

    def calculate_total_price(self):
        '''Calculate total price of fillup'''
        return round(decimal.Decimal(self.amount) * self.price, 2)

    def calculate_consumption(self):
        '''Calculate fuel consumption from previous full fillup'''
        if not self.tank_full:
            return None

        total_filled_amount = self.amount

        previous_full_fillup = Fillup.objects.filter(
            vehicle_id=self.vehicle.id,
            addition_date__lt=self.addition_date,
            tank_full=True,
        ).first()

        if previous_full_fillup is not None:
            total_distance_delta = self.distance - previous_full_fillup.distance

            if total_distance_delta <= 0:
                return None

            '''We need sum of amount from partial fillups between current and
            previous full fillups to calculate accurate consumption'''
            partial_filled_sum = Fillup.objects.filter(
                vehicle_id=self.vehicle.id,
                addition_date__lt=self.addition_date,
                pk__gt=previous_full_fillup.id,
            ).aggregate(sum_amount=Sum('amount'))

            if partial_filled_sum['sum_amount'] is not None:
                total_filled_amount += partial_filled_sum['sum_amount']

            return total_filled_amount / total_distance_delta * 100

        return None

    def save(self, *args, **kwargs):
        self.distance_delta = self.calculate_distance_delta()
        self.total_price = self.calculate_total_price()
        self.consumption = self.calculate_consumption()
        super(Fillup, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f'({self.vehicle}) {self.distance}, {self.amount} @ {self.price}'
