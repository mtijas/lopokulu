# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import User
from django.test import TestCase

from equipment.models import Equipment, EquipmentUser


class EquipmentModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.equipment = Equipment.objects.create(
            name="TestOwner", register_number="TEST-ADMINNER"
        )

    def test_correct_output_of_str(self):
        """Test that __str__ outputs correctly"""
        equipment = Equipment.objects.get(name="TestOwner")

        self.assertEqual("(TEST-ADMINNER) TestOwner", str(equipment))


class EquipmentUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        equipment = Equipment.objects.create(
            register_number="TE-1", name="TEST EQUIPMENT"
        )
        user = User.objects.create(username="user@foo.bar")
        EquipmentUser.objects.create(equipment=equipment, user=user)

    def test_default_role_is_READONLY(self):
        """Default role should be READONLY when attaching User to Equipment"""
        equipment = Equipment.objects.get(register_number="TE-1")
        user = User.objects.get(username="user@foo.bar")
        equipment_user = EquipmentUser.objects.get(equipment=equipment.id, user=user.id)

        self.assertEqual(equipment_user.role, "READ_ONLY")

    def test_role_USER_is_assignable(self):
        """EquipmentUser should have role USER assignable"""
        equipment = Equipment.objects.get(register_number="TE-1")
        user = User.objects.get(username="user@foo.bar")
        equipment_user = EquipmentUser.objects.create(
            equipment=equipment, user=user, role="USER"
        )

        self.assertEqual(equipment_user.role, "USER")

    def test_role_ADMIN_is_assignable(self):
        """EquipmentUser should have role ADMIN assignable"""
        equipment = Equipment.objects.get(register_number="TE-1")
        user = User.objects.get(username="user@foo.bar")
        equipment_user = EquipmentUser.objects.create(
            equipment=equipment, user=user, role="ADMIN"
        )

        self.assertEqual(equipment_user.role, "ADMIN")

    def test_str_outputs_correctly(self):
        """EquipmentUser __str__ should output correctly"""
        equipment = Equipment.objects.get(register_number="TE-1")
        user = User.objects.get(username="user@foo.bar")
        equipment_user = EquipmentUser.objects.get(equipment=equipment.id, user=user.id)
        expected = f"TEST EQUIPMENT has READ_ONLY user {user}"

        self.assertEqual(str(equipment_user), expected)
