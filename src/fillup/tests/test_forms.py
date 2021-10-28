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
        expected = {
            "vehicle": ["You are not allowed to report fillup for that vehicle"],
        }

        form = FillupForm(self.user, data={'vehicle': vehicle})

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_fillup_allowed_for_vehicle_driver(self):
        """Fillup is allowed for user with driver status on a vehicle"""
        vehicle = Vehicle.objects.create(name="TestDR", register_number="TEST-DR")
        vehicle_user = VehicleUser.objects.create(
            person=self.user, vehicle=vehicle, role="DR")
        expected = {}

        form = FillupForm(self.user, data={'vehicle': vehicle})

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # Vehicle should not be found
        self.assertNotIn("vehicle", form.errors)

    def test_fillup_allowed_for_vehicle_owner(self):
        """Fillup is allowed for user with owner status on a vehicle"""
        vehicle = Vehicle.objects.create(name="TestOW", register_number="TEST-OW")
        vehicle_user = VehicleUser.objects.create(
            person=self.user, vehicle=vehicle, role="OW")
        expected = {}

        form = FillupForm(self.user, data={'vehicle': vehicle})

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # Vehicle should not be found
        self.assertNotIn("vehicle", form.errors)
