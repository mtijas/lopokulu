# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from fillup.models import Fillup
from manager.models import Vehicle


class FillupModelTestCase(TestCase):
    def setUp(self):
        Vehicle.objects.create(name='TestOW', register_number='TEST-OW')

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
