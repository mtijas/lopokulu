# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase

from equipment.models import Equipment, EquipmentUser
from equipment.utils import user_has_role_for_equipment


class EquipmentUtilsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.nonauth_user = User.objects.create_user(
            username="nonauth_user@foo.bar", password="top_secret"
        )
        cls.ro_user = User.objects.create_user(
            username="ro_user@foo.bar", password="top_secret"
        )
        cls.user_user = User.objects.create_user(
            username="user_user@foo.bar", password="top_secret"
        )
        cls.admin_user = User.objects.create_user(
            username="admin_user@foo.bar", password="top_secret"
        )
        cls.equipment_test = Equipment.objects.create(
            name="TestEQ1",
            register_number="TEST-EQ1",
            allowed_measurements=["test"],
        )
        cls.equipment_na = Equipment.objects.create(
            name="TestEQNA",
            register_number="TEST-EQNA",
        )
        EquipmentUser.objects.create(
            user=cls.ro_user, equipment=cls.equipment_test, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.ro_user, equipment=cls.equipment_na, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user_user, equipment=cls.equipment_test, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.admin_user, equipment=cls.equipment_test, role="ADMIN"
        )

    def test_admin_user_should_return_true_with_defaults(self):
        """Admin user and type should result True with default attrs"""
        result = user_has_role_for_equipment(self.admin_user.id, "test")

        self.assertTrue(result)

    def test_user_user_should_return_true_with_defaults(self):
        """User user and type should result True with default attrs"""
        result = user_has_role_for_equipment(self.user_user.id, "test")

        self.assertTrue(result)

    def test_ro_user_should_return_false_with_defaults(self):
        """Read-only user and type should result False with default attrs"""
        result = user_has_role_for_equipment(self.ro_user.id, "test")

        self.assertFalse(result)

    def test_admin_user_should_return_false_for_nonexisting_type(self):
        """Admin user and type should result False for nonexisting type"""
        result = user_has_role_for_equipment(self.admin_user.id, "dummy")

        self.assertFalse(result)

    def test_nonauth_user_should_return_false_with_defaults(self):
        """Not-authed user and type should result False with default attrs"""
        result = user_has_role_for_equipment(self.nonauth_user.id, "test")

        self.assertFalse(result)

    def test_user_with_role_for_equipment_should_result_true(self):
        """User with role for specific equipment should result True"""
        result = user_has_role_for_equipment(
            self.admin_user.id, "test", self.equipment_test.id
        )

        self.assertTrue(result)

    def test_user_with_role_for_equipment_should_result_true_test_2(self):
        """User with role for specific equipment should result True, test 2"""
        result = user_has_role_for_equipment(
            self.ro_user.id, "test", self.equipment_test.id, ["READ_ONLY"]
        )

        self.assertTrue(result)

    def test_user_without_role_for_equipment_should_result_false(self):
        """User without role for specific equipment should result False"""
        result = user_has_role_for_equipment(
            self.admin_user.id, "test", self.equipment_na.id
        )

        self.assertFalse(result)

    def test_ro_user_should_return_true_with_ro_as_allowed_role(self):
        """Read-only user and type should result True with RO as allowed type"""
        result = user_has_role_for_equipment(
            self.ro_user.id, "test", allowed_roles=["READ_ONLY"]
        )

        self.assertTrue(result)
