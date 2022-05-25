# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from equipment.forms import EquipmentForm
from manager.models import Person
from equipment.models import Equipment, EquipmentUser


class EquipmentFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        cls.equipment1 = Equipment.objects.create(name='TestRO', register_number='TEST-RO')
        cls.equipment2 = Equipment.objects.create(name='TestUSER', register_number='TEST-USER')
        cls.equipment3 = Equipment.objects.create(name='TestADMIN', register_number='TEST-ADMIN')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment1, role='READONLY')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment2, role='USER')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment3, role='ADMIN')

    def setUp(self):
        self.base_form_data = {
            'name': 'base name',
            'register_number': 'base-register-num',
        }
