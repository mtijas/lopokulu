# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from fillup.forms import FillupForm
from manager.models import Person, Vehicle, VehicleUser
from fillup.models import Fillup


class FillupFormTestCase(TestCase):
    def setUp(self):
        self.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        Vehicle.objects.create(name='TestRO', register_number='TEST-RO')
        Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        Vehicle.objects.create(name='TestOW', register_number='TEST-OW')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestRO'), role='RO')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestDR'), role='DR')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestOW'), role='OW')
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=100,
            vehicle=Vehicle.objects.get(name='TestOW'),
        )
        self.base_form_data = {
            'price': 1,
            'amount': 1,
            'distance': 1,
            'vehicle': None,
        }

    def test_fillup_not_allowed_for_vehicle_readonly_user(self):
        '''Fillup is not allowed for user with readonly status on a vehicle'''
        expected = {
            'vehicle': ['You are not allowed to report fillup for that vehicle'],
        }
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestRO')

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_fillup_allowed_for_vehicle_driver(self):
        '''Fillup is allowed for user with driver status on a vehicle'''
        expected = {}
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestDR')

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # Vehicle should not be found in errors dictionary
        self.assertNotIn('vehicle', form.errors)

    def test_fillup_allowed_for_vehicle_owner(self):
        '''Fillup is allowed for user with owner status on a vehicle'''
        expected = {}
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestOW')

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # Vehicle should not be found
        self.assertNotIn('vehicle', form.errors)

    def test_negative_amount_not_allowed(self):
        '''Filled amount should not be negative'''
        expected = {
            'amount': ['Value should be over zero',]
        }
        data = self.base_form_data
        data['amount'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_amount_not_allowed(self):
        '''Filled amount should not be zero'''
        expected = {
            'amount': ['Value should be over zero',]
        }
        data = self.base_form_data
        data['amount'] = 0

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_amount_is_allowed(self):
        '''Positive number allowed for filled amount'''
        expected = {}
        data = self.base_form_data
        data['amount'] = 0.1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # Amount should not be found in errors dictionary
        self.assertNotIn('amount', form.errors)

    def test_negative_price_not_allowed(self):
        '''Filled price should not be negative'''
        expected = {
            'price': ['Value should be over zero',]
        }
        data = self.base_form_data
        data['price'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_price_not_allowed(self):
        '''Filled price should not be zero'''
        expected = {
            'price': ['Value should be over zero',]
        }
        data = self.base_form_data
        data['price'] = 0

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_price_is_allowed(self):
        '''Positive number allowed for filled price'''
        expected = {}
        data = self.base_form_data
        data['price'] = 0.1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # price should not be found in errors dictionary
        self.assertNotIn('price', form.errors)

    def test_negative_distance_not_allowed(self):
        '''Filled distance should not be negative'''
        expected = {
            'distance': ['Distance should be zero or more',]
        }
        data = self.base_form_data
        data['distance'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_distance_is_allowed(self):
        '''Filled distance should not be zero'''
        expected = {}
        data = self.base_form_data
        data['distance'] = 0

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # distance should not be found in errors dictionary
        self.assertNotIn('distance', form.errors)

    def test_positive_distance_is_allowed(self):
        '''Positive number allowed for filled distance'''
        expected = {}
        data = self.base_form_data
        data['distance'] = 0.1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
        # distance should not be found in errors dictionary
        self.assertNotIn('distance', form.errors)

    def test_distance_cannot_be_less_than_on_previous_fillup(self):
        '''New fillup distance cannot be less than distance of previous fillup'''
        expected = {
            'distance': ['Distance should be more than 100.0']
        }
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestOW')
        data['distance'] = 42

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)
