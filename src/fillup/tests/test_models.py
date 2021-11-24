# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from fillup.models import Fillup
from manager.models import Vehicle


class FillupModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.vehicle = Vehicle.objects.create(name='TestOW', register_number='TEST-OW')

    def test_correct_output_of_str(self):
        '''Test that __str__ outputs correctly'''
        vehicle = Vehicle.objects.get(name='TestOW')
        fillup = Fillup(
            price=2.013,
            amount=42,
            distance=100,
            vehicle=vehicle,
        )
        expected = f'({vehicle}) 100, 42 @ 2.013'

        result = str(fillup)

        self.assertEqual(expected, result)

    def test_distance_delta_is_distance_on_first_fillup(self):
        '''Distance delta should match distance on first fillup'''
        fillup = Fillup(
            price=2.013,
            amount=42,
            distance=200,
            vehicle=self.vehicle,
        )
        fillup.save()

        self.assertEqual(fillup.distance_delta, 200)

    def test_distance_delta_gets_calculated_on_save(self):
        '''Distance delta should be calculated on save'''
        # Add a fillup to get reliable distance delta expectation
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=100,
            vehicle=self.vehicle,
        )

        fillup = Fillup(
            price=2.013,
            amount=42,
            distance=200,
            vehicle=self.vehicle,
        )
        fillup.save()

        self.assertEqual(fillup.distance_delta, 100)

    def test_updating_fillup_updates_distance_delta_for_latest(self):
        '''Distance delta should be updated for latest row on updating'''
        vehicle = Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        # Add a couple of fillups to get reliable distance delta expectation
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=100,
            distance_delta=100,
            vehicle=vehicle,
        )
        target = Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=200,
            distance_delta=100,
            vehicle=vehicle,
        )

        target.distance = 150
        target.save()

        self.assertEqual(target.distance_delta, 50)

    def test_updating_fillup_updates_distance_delta_for_middle_row(self):
        '''Distance delta should be updated for middle row on updating'''
        vehicle = Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        # Add a couple of fillups to get reliable distance delta expectation
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=100,
            distance_delta=100,
            vehicle=vehicle,
        )
        target = Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=200,
            distance_delta=100,
            vehicle=vehicle,
        )
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=300,
            distance_delta=100,
            vehicle=vehicle,
        )

        target.distance = 160
        target.save()

        self.assertEqual(target.distance_delta, 60)
