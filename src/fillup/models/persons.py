from django.contrib.auth.models import User
from django.db import models

from .vehicles import Vehicle


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicles = models.ManyToManyField(Vehicle, through='VehicleUser')
