# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase

from equipment.models import Equipment, EquipmentUser
from fillup.forms import FillupForm
from fillup.models import Fillup


class FillupFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser@foo.bar", password="top_secret"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestREAD_ONLY",
            register_number="TEST-READ_ONLY",
            allowed_measurements=["fillup"],
        )
        cls.equipment2 = Equipment.objects.create(
            name="TestUSER",
            register_number="TEST-USER",
            allowed_measurements=["fillup"],
        )
        cls.equipment3 = Equipment.objects.create(
            name="TestADMIN",
            register_number="TEST-ADMIN",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment2, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment3, role="ADMIN"
        )
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=50,
            equipment=cls.equipment3,
            addition_date=datetime.fromisoformat("2022-06-15T15:00:00+02:00"),
        )
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment3,
            addition_date=datetime.fromisoformat("2022-06-15T16:00:00+02:00"),
        )
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=300,
            equipment=cls.equipment3,
            addition_date=datetime.fromisoformat("2022-06-15T17:00:00+02:00"),
        )

    def setUp(self):
        self.base_form_data = {
            "price": 1,
            "amount": 1,
            "distance": 1,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T17:00:00+02:00"
        }

    def test_fillup_not_allowed_for_equipment_without_fillup_allowed(self):
        """Fillup is not allowed for equipment without fillup allowed"""
        expected = {
            "equipment": [
                "Select a valid choice. That choice is not one of the available choices."
            ],
        }
        data = self.base_form_data
        data["equipment"] = Equipment.objects.create(
            name="TestNoFillup", register_number="TEST-NO-FILLUP"
        )
        EquipmentUser.objects.create(
            user=self.user, equipment=data["equipment"], role="ADMIN"
        )

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_fillup_not_allowed_for_equipment_readonly_user(self):
        """Fillup is not allowed for user with readonly status on a equipment"""
        expected = {
            "equipment": [
                "Select a valid choice. That choice is not one of the available choices."
            ],
        }
        data = self.base_form_data
        data["equipment"] = self.equipment1.id

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_fillup_allowed_for_equipment_driver(self):
        """Fillup is allowed for user with driver status on a equipment"""
        data = self.base_form_data
        data["equipment"] = self.equipment2.id

        form = FillupForm(self.user, data=data)

        # Equipment should not be found in errors dictionary
        self.assertNotIn("equipment", form.errors)

    def test_fillup_allowed_for_equipment_owner(self):
        """Fillup is allowed for user with owner status on a equipment"""
        data = self.base_form_data
        data["equipment"] = self.equipment3.id

        form = FillupForm(self.user, data=data)

        # Equipment should not be found
        self.assertNotIn("equipment", form.errors)

    def test_fillup_not_allowed_for_non_existing_equipment(self):
        """Fillup is not allowed for non-existing equipment"""
        expected = {
            "equipment": [
                "Select a valid choice. That choice is not one of the available choices."
            ],
        }
        data = self.base_form_data
        data["equipment"] = 543214321

        form = FillupForm(self.user, data=data)

        # We only want to test for expected key-value pairs
        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_negative_amount_not_allowed(self):
        """Filled amount should not be negative"""
        expected = {"amount": ["Value should be over zero"]}
        data = self.base_form_data
        data["equipment"] = self.equipment2
        data["amount"] = -1

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_amount_not_allowed(self):
        """Filled amount should not be zero"""
        expected = {"amount": ["Value should be over zero"]}
        data = self.base_form_data
        data["amount"] = 0

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_amount_is_allowed(self):
        """Positive number allowed for filled amount"""
        data = self.base_form_data
        data["amount"] = 0.1

        form = FillupForm(self.user, data=data)

        # Amount should not be found in errors dictionary
        self.assertNotIn("amount", form.errors)

    def test_negative_price_not_allowed(self):
        """Filled price should not be negative"""
        expected = {"price": ["Value should be over zero"]}
        data = self.base_form_data
        data["price"] = -1

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_price_not_allowed(self):
        """Filled price should not be zero"""
        expected = {"price": ["Value should be over zero"]}
        data = self.base_form_data
        data["price"] = 0

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_positive_price_is_allowed(self):
        """Positive number allowed for filled price"""
        data = self.base_form_data
        data["price"] = 0.1

        form = FillupForm(self.user, data=data)

        # price should not be found in errors dictionary
        self.assertNotIn("price", form.errors)

    def test_negative_distance_not_allowed(self):
        """Filled distance should not be negative"""
        expected = {"distance": ["Distance should be zero or more"]}
        data = self.base_form_data
        data["distance"] = -1
        data["equipment"] = self.equipment2

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_zero_distance_is_allowed(self):
        """Zero filled distance should be allowed"""
        data = self.base_form_data
        data["distance"] = 0
        data["equipment"] = self.equipment2

        form = FillupForm(self.user, data=data)

        # distance should not be found in errors dictionary
        self.assertNotIn("distance", form.errors)

    def test_positive_distance_is_allowed(self):
        """Positive number allowed for filled distance"""
        data = self.base_form_data
        data["distance"] = 0.1
        data["equipment"] = self.equipment2

        form = FillupForm(self.user, data=data)

        # distance should not be found in errors dictionary
        self.assertNotIn("distance", form.errors)

    def test_distance_cannot_be_less_than_on_previous_fillup(self):
        """New fillup distance cannot be less than distance of previous fillup"""
        expected = {"distance": ["Distance should be more than 300.0"]}
        data = self.base_form_data
        data["equipment"] = self.equipment3.id
        data["addition_date"] = "2022-06-15 18:00:00+02:00"
        data["distance"] = 42

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_distance_must_be_less_than_on_next_fillup(self):
        """New fillup distance must be less than distance of next fillup"""
        expected = {"distance": ["Distance should be less than 100.0"]}
        data = self.base_form_data
        data["equipment"] = self.equipment3.id
        data["distance"] = 175
        data["addition_date"] = "2022-06-15 15:30:00+02:00"

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_price_cant_have_over_three_decimals(self):
        """Price should not have over three decimals"""
        expected = {"price": ["Ensure that there are no more than 3 decimal places."]}
        data = self.base_form_data
        data["price"] = 1.3243

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_price_cant_be_over_five_digits_long(self):
        """Price should not be over five digits long"""
        expected = {"price": ["Ensure that there are no more than 5 digits in total."]}
        data = self.base_form_data
        data["price"] = 132.324

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_price_with_five_digits_allowed(self):
        """Price with five digits should be allowed"""
        data = self.base_form_data
        data["price"] = 99.999

        form = FillupForm(self.user, data=data)

        self.assertNotIn("price", form.errors)

    def test_lowest_price_of_0_001_allowed(self):
        """Price of 0.001 should be allowed"""
        data = self.base_form_data
        data["price"] = 0.001

        form = FillupForm(self.user, data=data)

        self.assertNotIn("price", form.errors)

    def test_price_cant_have_hundreds(self):
        """Price should not have hundreds"""
        expected = {
            "price": [
                "Ensure that there are no more than 2 digits before the decimal point."
            ]
        }
        data = self.base_form_data
        data["price"] = 132

        form = FillupForm(self.user, data=data)

        subset = {k: v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_equipment_is_preselected_on_existing_equipment_id(self):
        """Equipment should be preselected on initial data"""
        initial_data = {
            "equipment": self.equipment2.id,
        }
        expected_html_0 = f'<input type="radio" name="equipment" value="{self.equipment2.id}" required id="id_equipment_0" checked>'
        expected_html_1 = f'<input type="radio" name="equipment" value="{self.equipment3.id}" required id="id_equipment_1">'

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html_0, str(form), 1)
        self.assertInHTML(expected_html_1, str(form), 1)

    def test_equipment_is_preselected_on_existing_equipment_id_2(self):
        """Equipment should be preselected on different initial data"""
        initial_data = {
            "equipment": self.equipment3.id,
        }
        expected_html_0 = f'<input type="radio" name="equipment" value="{self.equipment2.id}" required id="id_equipment_0">'
        expected_html_1 = f'<input type="radio" name="equipment" value="{self.equipment3.id}" required id="id_equipment_1" checked>'

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html_0, str(form), 1)
        self.assertInHTML(expected_html_1, str(form), 1)

    def test_equipment_is_not_preselected_on_non_existing_equipment_id(self):
        """First equipment should be selected on non-existing initial equipment id"""
        initial_data = {
            "equipment": 9877676,
        }
        expected_html_0 = f'<input type="radio" name="equipment" value="{self.equipment2.id}" required id="id_equipment_0">'
        expected_html_1 = f'<input type="radio" name="equipment" value="{self.equipment3.id}" required id="id_equipment_1">'

        form = FillupForm(self.user, initial=initial_data)

        self.assertInHTML(expected_html_0, str(form), 1)
        self.assertInHTML(expected_html_1, str(form), 1)

    def test_equipment_is_preselected_without_initial_data(self):
        """Equipment should be preselected without initial data"""
        expected_html_0 = f'<input type="radio" name="equipment" value="{self.equipment2.id}" required id="id_equipment_0" checked>'
        expected_html_1 = f'<input type="radio" name="equipment" value="{self.equipment3.id}" required id="id_equipment_1">'

        form = FillupForm(self.user)

        self.assertInHTML(expected_html_0, str(form), 1)
        self.assertInHTML(expected_html_1, str(form), 1)
