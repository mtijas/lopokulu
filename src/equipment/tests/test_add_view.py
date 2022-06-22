# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser

class EquipmentAddViewAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1@foo.bar", password="top_secret1"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO"
        )
        cls.equipmentuser1 = EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment1, role="READ_ONLY"
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

    def test_respond_with_200_for_get_equipment_add(self):
        """Response 200 should be given on get /equipment/add/"""
        self.user1.user_permissions.add(self.permissions["add"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/add/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment_add(self):
        """Non-logged-in users should get redirected to login on equipment/add view"""
        response = self.client.get("/equipment/add/")

        self.assertRedirects(response, "/accounts/login/?next=/equipment/add/")

class EquipmentAddViewBasicTestCase(TestCase):
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

    def test_redirect_to_equipment_detail_view_after_successful_addition(self):
        """User should be redirected to Equipment detail view after successful equipment addition"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {
            "name": "New Test Equipment EQ1",
            "register_number": "TEST-EQ1",
        }
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.post("/equipment/add/", data=data, follow=True)

        self.assertContains(response, data["name"])

    def test_returned_to_equipmentform_on_invalid_data(self):
        """User should be returned to add_equipment view on posting invalid data"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {}
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.post("/equipment/add/", data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "equipment/add.html")

    def test_permissions_saved_on_form_save(self):
        """Permissions should be saved when a new Equipment is added"""
        self.user1.user_permissions.add(self.permissions["add"])
        data = {
            "name": "test-1",
            "register_number": "REG-T1",
        }
        data[f"perm-{self.user1.id}"] = "NOACCESS"
        data[f"perm-{self.user2.id}"] = "NOACCESS"
        data[f"perm-{self.user3.id}"] = "READ_ONLY"

        self.client.login(username="testuser1@foo.bar", password="top_secret1")
        response = self.client.post("/equipment/add/", data=data)

        saved_equipment = Equipment.objects.get(register_number="REG-T1")
        saved_perms = EquipmentUser.objects.filter(equipment=saved_equipment)

        # Login user should get ADMIN privs since no admin is assigned at post data.
        expected_perms = [
            str(
                EquipmentUser(
                    user=self.user3, equipment=saved_equipment, role="READ_ONLY"
                )
            ),
            str(
                EquipmentUser(user=self.user1, equipment=saved_equipment, role="ADMIN")
            ),
        ]

        self.assertQuerysetEqual(list(saved_perms), expected_perms, transform=str)
