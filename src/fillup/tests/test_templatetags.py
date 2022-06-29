# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.utils.timezone import now

from equipment.models import Equipment, EquipmentUser
from fillup.models import Fillup
from fillup.templatetags import partials


class StatsCardTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.equipment = Equipment.objects.create(
            name="TestEQ1",
            register_number="TEST-EQ1",
            allowed_measurements=["fillup"],
        )
        Fillup.objects.create(
            price=Decimal(2.1),
            amount=10,
            distance=100,
            equipment=cls.equipment,
            addition_date=now() - timedelta(days=32),
            tank_full=True,
        )
        Fillup.objects.create(
            price=Decimal(2.2),
            amount=15,
            distance=200,
            equipment=cls.equipment,
            addition_date=now() - timedelta(days=8),
            tank_full=True,
        )
        Fillup.objects.create(
            price=Decimal(2.3),
            amount=20,
            distance=300,
            equipment=cls.equipment,
            addition_date=now() - timedelta(days=7),
            tank_full=True,
        )
        Fillup.objects.create(
            price=Decimal(2.4),
            amount=20,
            distance=350,
            equipment=cls.equipment,
            addition_date=now() - timedelta(days=7),
            tank_full=False,
        )
        Fillup.objects.create(
            price=Decimal(2.4),
            amount=15,
            distance=400,
            equipment=cls.equipment,
            addition_date=now() - timedelta(days=4),
            tank_full=True,
        )

    def test_returns_31d_stats_for_equipment_as_default(self):
        """31 day stats for single Equipment should be returned as default"""
        response = partials.fillup_equipment_stats(self.equipment)

        self.assertAlmostEqual(float(response["stats"]["consumption__avg"]), 23.333, places=3)
        self.assertAlmostEqual(float(response["stats"]["distance_delta__sum"]), 300, places=1)
        self.assertAlmostEqual(float(response["stats"]["total_price__sum"]), 163, places=1)

    def test_returns_proper_stats_for_equipment_on_custom_days_limit(self):
        """Start datetime should be customizable, testing with 180 days"""
        start_dt = now() - timedelta(days=180)

        response = partials.fillup_equipment_stats(self.equipment, start_dt)

        self.assertAlmostEqual(float(response["stats"]["consumption__avg"]), 23.333, places=3)
        self.assertAlmostEqual(float(response["stats"]["distance_delta__sum"]), 400, places=1)
        self.assertAlmostEqual(float(response["stats"]["total_price__sum"]), 184, places=1)

    def test_returns_proper_stats_for_equipment_on_custom_days_limit_test_2(self):
        """Stop datetime should be customizable"""
        start_dt = now() - timedelta(days=35)
        stop_dt = now() - timedelta(days=8)

        response = partials.fillup_equipment_stats(self.equipment, start_dt, stop_dt)

        self.assertAlmostEqual(float(response["stats"]["consumption__avg"]), 15, places=3)
        self.assertAlmostEqual(float(response["stats"]["distance_delta__sum"]), 200, places=1)
        self.assertAlmostEqual(float(response["stats"]["total_price__sum"]), 54, places=1)

    def test_returns_zeros_when_no_fillups_found(self):
        """Zeroes should be returned if no statistics found for given time range"""
        start_dt = now() - timedelta(days=1)

        response = partials.fillup_equipment_stats(self.equipment, start_dt)

        self.assertEqual(float(response["stats"]["distance_delta__sum"]), 0)
        self.assertEqual(float(response["stats"]["consumption__avg"]), 0)
        self.assertEqual(float(response["stats"]["total_price__sum"]), 0)
