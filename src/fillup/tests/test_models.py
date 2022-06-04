# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from decimal import Decimal

from django.test import TestCase

from equipment.models import Equipment
from fillup.models import Fillup


class FillupModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.equipment = Equipment.objects.create(
            name="TestOW", register_number="TEST-OW"
        )

    def test_correct_output_of_str(self):
        """Test that __str__ outputs correctly"""
        equipment = Equipment.objects.get(name="TestOW")
        fillup = Fillup(
            price=2.013,
            amount=42,
            distance=100,
            equipment=equipment,
        )
        expected = f"({equipment}) 100, 42 @ 2.013"

        result = str(fillup)

        self.assertEqual(expected, result)

    def test_distance_delta_is_distance_on_first_fillup(self):
        """Distance delta should match distance on first fillup"""
        fillup = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=200,
            equipment=self.equipment,
        )
        fillup.save()

        self.assertEqual(fillup.distance_delta, 200)

    def test_distance_delta_gets_calculated_on_save(self):
        """Distance delta should be calculated on save"""
        # Add a fillup to get reliable distance delta expectation
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
        )

        fillup = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=200,
            equipment=self.equipment,
        )
        fillup.save()

        self.assertEqual(fillup.distance_delta, 100)

    def test_updating_fillup_updates_distance_delta_for_latest(self):
        """Distance delta should be updated for latest row on updating"""
        equipment = Equipment.objects.create(name="TestDR", register_number="TEST-DR")
        # Add a couple of fillups to get reliable distance delta expectation
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            distance_delta=100,
            equipment=equipment,
        )
        target = Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=200,
            distance_delta=100,
            equipment=equipment,
        )

        target.distance = 150
        target.save()

        self.assertEqual(target.distance_delta, 50)

    def test_updating_fillup_updates_distance_delta_for_middle_row(self):
        """Distance delta should be updated for middle row on updating"""
        equipment = Equipment.objects.create(name="TestDR", register_number="TEST-DR")
        # Add a couple of fillups to get reliable distance delta expectation
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            distance_delta=100,
            equipment=equipment,
        )
        target = Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=200,
            distance_delta=100,
            equipment=equipment,
        )
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=300,
            distance_delta=100,
            equipment=equipment,
        )

        target.distance = 160
        target.save()

        self.assertEqual(target.distance_delta, 60)

    def test_total_price_gets_properly_calculated(self):
        """Total price should get calculated"""
        fillup1 = Fillup(
            price=Decimal(2),
            amount=42,
            distance=200,
            equipment=self.equipment,
        )
        fillup2 = Fillup(
            price=Decimal(1.5),
            amount=42,
            distance=200,
            equipment=self.equipment,
        )
        fillup3 = Fillup(
            price=Decimal(1.785),
            amount=10,
            distance=200,
            equipment=self.equipment,
        )

        fillup1.save()
        fillup2.save()
        fillup3.save()

        self.assertAlmostEqual(float(fillup1.total_price), 84.0, places=2)
        self.assertAlmostEqual(float(fillup2.total_price), 63.0, places=2)
        self.assertAlmostEqual(float(fillup3.total_price), 17.85, places=2)

    def test_total_price_gets_rounded_to_two_decimals(self):
        """Total price should be rounded to two decimals"""
        fillup1 = Fillup(
            price=Decimal(1.848),
            amount=18.3,
            distance=200,
            equipment=self.equipment,
        )

        fillup1.save()

        self.assertAlmostEqual(float(fillup1.total_price), 33.82, places=2)

    def test_consumption_calculated_from_two_consecutive_full_fills(self):
        """Consumption should be calculated from two consecutive full fillups"""
        fillup1 = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
            tank_full=True,
        )
        fillup2 = Fillup(
            price=Decimal(1.988),
            amount=11.48,
            distance=250,
            equipment=self.equipment,
            tank_full=True,
        )

        fillup1.save()
        fillup2.save()

        self.assertAlmostEqual(float(fillup2.consumption), 7.653, places=3)

    def test_consumption_None_for_partial_fill(self):
        """Consumption should be None for partial fills"""
        fillup1 = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
            tank_full=False,
        )

        fillup1.save()

        self.assertEqual(fillup1.consumption, None)

    def test_consumption_calculated_correctly_when_one_partial_fill_before(self):
        """Consumption should be calculated from two full fillups with partial
        fill in between
        """
        fillup1 = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
            tank_full=True,
        )
        fillup2 = Fillup(
            price=Decimal(1.988),
            amount=9,
            distance=200,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup3 = Fillup(
            price=Decimal(1.8),
            amount=5,
            distance=250,
            equipment=self.equipment,
            tank_full=True,
        )

        fillup1.save()
        fillup2.save()
        fillup3.save()

        self.assertAlmostEqual(float(fillup3.consumption), 9.333, places=3)

    def test_consumption_correct_when_multiple_partial_fill_before(self):
        """Consumption should be calculated from two full fillups with multiple
        partial fills in between
        """
        fillup1 = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
            tank_full=True,
        )
        fillup2 = Fillup(
            price=Decimal(1.988),
            amount=9,
            distance=200,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup3 = Fillup(
            price=Decimal(1.988),
            amount=4.5,
            distance=250,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup4 = Fillup(
            price=Decimal(1.988),
            amount=5.5,
            distance=300,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup5 = Fillup(
            price=Decimal(1.8),
            amount=18,
            distance=600,
            equipment=self.equipment,
            tank_full=True,
        )

        fillup1.save()
        fillup2.save()
        fillup3.save()
        fillup4.save()
        fillup5.save()

        self.assertAlmostEqual(float(fillup5.consumption), 7.4, places=3)

    def test_consumption_none_when_only_one_full_fillup(self):
        """Consumption should be none when only one full fillup"""
        fillup1 = Fillup(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup2 = Fillup(
            price=Decimal(1.988),
            amount=9,
            distance=200,
            equipment=self.equipment,
            tank_full=False,
        )
        fillup3 = Fillup(
            price=Decimal(1.8),
            amount=5,
            distance=250,
            equipment=self.equipment,
            tank_full=True,
        )

        fillup1.save()
        fillup2.save()
        fillup3.save()

        self.assertEqual(fillup3.consumption, None)
