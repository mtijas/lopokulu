# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser

class EquipmentDeleteViewAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1@foo.bar", password="top_secret1"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO"
        )

        # Create groups and permissions
        ct = ContentType.objects.get_for_model(Equipment)
        cls.permissions = dict()
        cls.permissions["add"], _ = Permission.objects.get_or_create(
            codename="add_equipment", content_type=ct
        )
        cls.permissions["edit"], _ = Permission.objects.get_or_create(
            codename="edit_equipment", content_type=ct
        )
        cls.permissions["view"], _ = Permission.objects.get_or_create(
            codename="view_equipment", content_type=ct
        )
        cls.permissions["delete"], _ = Permission.objects.get_or_create(
            codename="delete_equipment", content_type=ct
        )

    def setUp(self):
        self.client = Client()

    def test_delete_permission_allows_delete(self):
        """User with delete permission should be able to delete Equipment"""
        self.user1.user_permissions.add(self.permissions["delete"])
        with self.assertNumQueries(1):
            saved_equipment = Equipment.objects.create(
                name="test-delete-1", register_number="T-DEL-1"
            )

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.get(f"/equipment/{saved_equipment.id}/delete/")

        self.assertRedirects(response, f"/equipment/")
        self.assertFalse(Equipment.objects.filter(id=saved_equipment.id).exists())

    def test_delete_permission_required(self):
        """User with no perms should receive 403"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/delete/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Equipment.objects.filter(id=self.equipment1.id).exists())


class EquipmentDeleteViewBasicTestCase(TestCase):
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
        cls.equipmentuser1 = EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment1, role="READ_ONLY"
        )
        cls.equipmentuser2 = EquipmentUser.objects.create(
            user=cls.user2, equipment=cls.equipment2, role="USER"
        )
        cls.equipmentuser3 = EquipmentUser.objects.create(
            user=cls.user3, equipment=cls.equipment3, role="ADMIN"
        )

        # Create groups and permissions
        ct = ContentType.objects.get_for_model(Equipment)
        cls.permissions = dict()
        cls.permissions["add"], _ = Permission.objects.get_or_create(
            codename="add_equipment", content_type=ct
        )
        cls.permissions["edit"], _ = Permission.objects.get_or_create(
            codename="edit_equipment", content_type=ct
        )
        cls.permissions["view"], _ = Permission.objects.get_or_create(
            codename="view_equipment", content_type=ct
        )
        cls.permissions["delete"], _ = Permission.objects.get_or_create(
            codename="delete_equipment", content_type=ct
        )

    def setUp(self):
        self.client = Client()
