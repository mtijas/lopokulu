# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser


class EquipmentEditViewAuthTestCase(TestCase):
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

    def test_edit_permission_allows_getting_edit_form(self):
        """Response 200 should be given on url /equipment/<pk>/edit/ for ADMIN"""
        self.user3.user_permissions.add(self.permissions["edit"])
        self.client.login(username="testuser3@foo.bar", password="top_secret3")

        response = self.client.get(f"/equipment/{self.equipment3.id}/edit/")

        self.assertEqual(response.status_code, 200)

    def test_edit_permission_required_for_get(self):
        """User with no perms should receive 403"""
        self.client.login(username="testuser2@foo.bar", password="top_secret2")

        response = self.client.get(f"/equipment/{self.equipment3.id}/edit/")

        self.assertEqual(response.status_code, 403)

    def test_logged_out_user_gets_redirected_on_get_edit_form(self):
        """Non logged in user should get redirected on get"""
        response = self.client.get(f"/equipment/{self.equipment1.id}/edit/")

        self.assertRedirects(
            response, f"/accounts/login/?next=/equipment/{self.equipment1.id}/edit/"
        )

    def test_posting_to_edit_without_perms_should_not_actually_edit(self):
        """POSTing to edit view should need permissions"""
        data = {
            "name": "edited...",
            "register_number": "T-NO-PERM",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "ADMIN"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{self.equipment1.id}/edit/", data=data)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.equipment1.name, "TestRO")

    def test_posting_to_edit_should_get_logged_out_user_redirected(self):
        """POSTing to edit view should get logged out user redirected"""
        response = self.client.post(
            f"/equipment/{self.equipment1.id}/edit/", data=dict()
        )

        self.assertRedirects(
            response, f"/accounts/login/?next=/equipment/{self.equipment1.id}/edit/"
        )

    # Working edit permission is tested in case below


class EquipmentEditViewBasicTestCase(TestCase):
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

    def test_permissions_removed_only_for_current_equipment(self):
        """Permissions should be removed only from current equipment on save"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        saved_perms = EquipmentUser.objects.filter(equipment=self.equipment1)
        expected_perms = [str(self.equipmentuser1)]

        self.assertQuerysetEqual(list(saved_perms), expected_perms, transform=str)

    def test_permissions_updated_on_form_save(self):
        """Permissions should be updated when a Equipment is modified"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "USER"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "ADMIN"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user1, equipment=saved_equipment, role="USER")),
            str(
                EquipmentUser(user=self.user3, equipment=saved_equipment, role="ADMIN")
            ),
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_old_permissions_deleted_on_form_save_and_admin_assigned(self):
        """Old permissions should be deleted when a Equipment is modified and ADMIN added"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user1, equipment=saved_equipment, role="ADMIN"))
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_current_user_does_not_get_admin_if_admin_already_present(self):
        """Current user should not get automatic admin privs if another user has admins"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "ADMIN"
        data[f"perm-{self.user3.id}"] = "NOACCESS"

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post(f"/equipment/{saved_equipment.id}/edit/", data=data)

        # Update our equipment var with new data from form save
        saved_equipment = Equipment.objects.get(register_number="REG-T2")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)
        expected_perms = [
            str(EquipmentUser(user=self.user2, equipment=saved_equipment, role="ADMIN"))
        ]

        self.assertRedirects(response, f"/equipment/{saved_equipment.id}/")
        self.assertQuerysetEqual(
            list(saved_perms), expected_perms, ordered=False, transform=str
        )

    def test_permissions_get_prepopulated_on_edit(self):
        """Permission radio buttons should get prepopulated on edit"""
        self.user1.user_permissions.add(self.permissions["edit"])
        data = {
            "name": "test-2",
            "register_number": "REG-T2",
        }

        saved_equipment = Equipment.objects.create(
            name=data["name"], register_number=data["register_number"]
        )
        self.create_dummy_equipment_users(saved_equipment)

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.get(f"/equipment/{saved_equipment.id}/edit/")

        self.assertInHTML(
            f'<input type="radio" id="{self.user1.id}-READ_ONLY" name="perm-{self.user1.id}" value="READ_ONLY" checked>',
            response.content.decode(),
            1,
        )
        self.assertInHTML(
            f'<input type="radio" id="{self.user2.id}-ADMIN" name="perm-{self.user2.id}" value="ADMIN" checked>',
            response.content.decode(),
            1,
        )
        self.assertInHTML(
            f'<input type="radio" id="{self.user3.id}-READ_ONLY" name="perm-{self.user3.id}" value="READ_ONLY" checked>',
            response.content.decode(),
            1,
        )

    def create_dummy_equipment_users(self, equipment):
        """Create dummy equipment users for equipment"""
        EquipmentUser.objects.create(
            user=self.user1, equipment=equipment, role="READ_ONLY"
        )
        EquipmentUser.objects.create(user=self.user2, equipment=equipment, role="ADMIN")
        EquipmentUser.objects.create(
            user=self.user3, equipment=equipment, role="READ_ONLY"
        )
