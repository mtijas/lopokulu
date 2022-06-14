# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

from equipment.forms import EquipmentForm
from equipment.models import Equipment, EquipmentUser


class EquipmentFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1@foo.bar", password="top_secret1"
        )
        cls.user2 = User.objects.create_user(
            username="testuser2@foo.bar", password="top_secret2"
        )
        cls.user3 = User.objects.create_user(
            username="testuser3@foo.bar", password="top_secret3"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO"
        )
        cls.equipment2 = Equipment.objects.create(
            name="TestUSER", register_number="TEST-USER"
        )
        cls.equipment3 = Equipment.objects.create(
            name="TestADMIN", register_number="TEST-ADMIN"
        )
        EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment1, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment2, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment3, role="ADMIN"
        )

    def setUp(self):
        self.base_form_data = {
            "name": "base name",
            "register_number": "base-register-num",
        }

    def test_allowed_measurements_input_fields_generated_for_all_installed(self):
        """All installed measurement apps should have checkboxes on allowed measurements form"""
        form = EquipmentForm(self.user1)

        for index, app in enumerate(settings.INSTALLED_MEASUREMENT_APPS):
            needle = f'<input type="checkbox" name="allowed_measurements" value="{app}" id="id_allowed_measurements_{index}">'
            self.assertInHTML(needle, str(form), 1)
