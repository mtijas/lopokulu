# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from fillup.forms import FillupForm
from manager.models import Person, Vehicle, VehicleUser
from fillup.models import Fillup
from decimal import Decimal


class FillupFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        cls.vehicle1 = Vehicle.objects.create(name='TestRO', register_number='TEST-RO')
        cls.vehicle2 = Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        cls.vehicle3 = Vehicle.objects.create(name='TestOW', register_number='TEST-OW')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle1, role='RO')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle2, role='DR')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle3, role='OW')
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            vehicle=cls.vehicle3,
        )

    def setUp(self):
        self.base_form_data = {
            'price': 1,
            'amount': 1,
            'distance': 1,
            'vehicle': None,
        }

    def test_fillup_not_allowed_for_vehicle_readonly_user(self):
        '''Fillup is not allowed for user with readonly status on a vehicle'''
        expected = {
            'vehicle': ['Select a valid choice. That choice is not one of the available choices.'],
        }
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestRO')

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_fillup_allowed_for_vehicle_driver(self):
        '''Fillup is allowed for user with driver status on a vehicle'''
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestDR')

        form = FillupForm(self.user, data=data)

        # Vehicle should not be found in errors dictionary
        self.assertNotIn('vehicle', form.errors)

    def test_fillup_allowed_for_vehicle_owner(self):
        '''Fillup is allowed for user with owner status on a vehicle'''
        data = self.base_form_data
        data['vehicle'] = Vehicle.objects.get(name='TestOW')

        form = FillupForm(self.user, data=data)

        # Vehicle should not be found
        self.assertNotIn('vehicle', form.errors)

    def test_fillup_not_allowed_for_non_existing_vehicle(self):
        '''Fillup is not allowed for non-existing vehicle'''
        expected = {
            'vehicle': ['Select a valid choice. That choice is not one of the available choices.'],
        }
        data = self.base_form_data
        data['vehicle'] = 543214321

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_negative_amount_not_allowed(self):
        '''Filled amount should not be negative'''
        expected = {
            'amount': ['Value should be over zero']
        }
        data = self.base_form_data
        data['amount'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_amount_not_allowed(self):
        '''Filled amount should not be zero'''
        expected = {
            'amount': ['Value should be over zero']
        }
        data = self.base_form_data
        data['amount'] = 0

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_amount_is_allowed(self):
        '''Positive number allowed for filled amount'''
        data = self.base_form_data
        data['amount'] = 0.1

        form = FillupForm(self.user, data=data)

        # Amount should not be found in errors dictionary
        self.assertNotIn('amount', form.errors)

    def test_negative_price_not_allowed(self):
        '''Filled price should not be negative'''
        expected = {
            'price': ['Value should be over zero']
        }
        data = self.base_form_data
        data['price'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_price_not_allowed(self):
        '''Filled price should not be zero'''
        expected = {
            'price': ['Value should be over zero']
        }
        data = self.base_form_data
        data['price'] = 0

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_price_is_allowed(self):
        '''Positive number allowed for filled price'''
        data = self.base_form_data
        data['price'] = 0.1

        form = FillupForm(self.user, data=data)

        # price should not be found in errors dictionary
        self.assertNotIn('price', form.errors)

    def test_negative_distance_not_allowed(self):
        '''Filled distance should not be negative'''
        expected = {
            'distance': ['Distance should be zero or more']
        }
        data = self.base_form_data
        data['distance'] = -1

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_distance_is_not_allowed(self):
        '''Filled distance should not be zero'''
        data = self.base_form_data
        data['distance'] = 0

        form = FillupForm(self.user, data=data)

        # distance should not be found in errors dictionary
        self.assertNotIn('distance', form.errors)

    def test_positive_distance_is_allowed(self):
        '''Positive number allowed for filled distance'''
        data = self.base_form_data
        data['distance'] = 0.1

        form = FillupForm(self.user, data=data)

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

    def test_price_cant_have_over_three_decimals(self):
        '''Price should not have over three decimals'''
        expected = {
            'price': ['Ensure that there are no more than 3 decimal places.']
        }
        data = self.base_form_data
        data['price'] = 1.3243

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_price_cant_be_over_five_digits_long(self):
        '''Price should not be over five digits long'''
        expected = {
            'price': ['Ensure that there are no more than 5 digits in total.']
        }
        data = self.base_form_data
        data['price'] = 132.324

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_price_with_five_digits_allowed(self):
        '''Price with five digits should be allowed'''
        data = self.base_form_data
        data['price'] = 99.999

        form = FillupForm(self.user, data=data)

        self.assertNotIn('price', form.errors)

    def test_lowest_price_of_0_001_allowed(self):
        '''Price of 0.001 should be allowed'''
        data = self.base_form_data
        data['price'] = 0.001

        form = FillupForm(self.user, data=data)

        self.assertNotIn('price', form.errors)

    def test_price_cant_have_hundreds(self):
        '''Price should not have hundreds'''
        expected = {
            'price': ['Ensure that there are no more than 2 digits before the decimal point.']
        }
        data = self.base_form_data
        data['price'] = 132

        form = FillupForm(self.user, data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_vehicle_is_preselected_on_existing_vehicle_id(self):
        '''Vehicle should be preselected on initial data'''
        initial_data = {
            'vehicle': self.vehicle2.id,
        }
        expected_html = (
            f'''<ul id="id_vehicle">\n
                    <li><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0" checked>\n
                        {str(self.vehicle2)}</label>\n\n
                    </li>\n
                    <li><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1">\n
                        {str(self.vehicle3)}</label>\n\n
                    </li>\n
                </ul>
            '''
        )

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html, str(form), 1)

    def test_vehicle_is_preselected_on_existing_vehicle_id_2(self):
        '''Vehicle should be preselected on different initial data'''
        initial_data = {
            'vehicle': self.vehicle3.id,
        }
        expected_html = (
            f'''<ul id="id_vehicle">\n
                    <li><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0">\n
                        {str(self.vehicle2)}</label>\n\n
                    </li>\n
                    <li><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1" checked>\n
                        {str(self.vehicle3)}</label>\n\n
                    </li>\n
                </ul>
            '''
        )

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html, str(form), 1)

    def test_vehicle_is_not_preselected_on_non_existing_vehicle_id(self):
        '''First vehicle should be selected on non-existing initial vehicle id'''
        initial_data = {
            'vehicle': 9877676,
        }
        expected_html = (
            f'''<ul id="id_vehicle">
                    <li><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0">
                        {str(self.vehicle2)}</label>
                    </li>
                    <li><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1">
                        {str(self.vehicle3)}</label>
                    </li>
                </ul>
            '''
        )

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html, str(form), 1)

    def test_vehicle_is_preselected_without_initial_data(self):
        '''Vehicle should be preselected without initial data'''
        expected_html = (
            f'''<ul id="id_vehicle">\n
                    <li><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0" checked>\n
                        {str(self.vehicle2)}</label>\n\n
                    </li>\n
                    <li><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1">\n
                        {str(self.vehicle3)}</label>\n\n
                    </li>\n
                </ul>
            '''
        )

        form = FillupForm(self.user)

        self.assertInHTML(expected_html, str(form), 1)
