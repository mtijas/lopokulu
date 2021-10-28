# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from fillup.forms import FillupForm
from manager.models import Person, Vehicle, VehicleUser


class FillupFormTestCase(TestCase):
    def setUp(self):
        self.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')

    def test_fillup_not_allowed_for_vehicle_readonly_user(self):
        """Fillup is not allowed for user with readonly status on a vehicle"""
        vehicle = Vehicle.objects.create(name="TestRO", register_number="TEST-RO")
        vehicle_user = VehicleUser.objects.create(
            person=self.user, vehicle=vehicle, role="RO")

        form = FillupForm(
            self.user,
            data={
                'price': 12.34,
                'amount': 43.21,
                'distance': 100000,
                'vehicle': vehicle,
            }
        )

        self.assertEqual(
            form.errors["vehicle"], ["You are not allowed to report fillup for that vehicle"]
        )
