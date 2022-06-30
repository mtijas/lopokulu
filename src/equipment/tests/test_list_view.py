# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser

class EquipmentListViewAuthTestCase(TestCase):
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

    def setUp(self):
        self.client = Client()

    def test_respond_with_200_for_url_equipment(self):
        """Response 200 should be given on url /equipment/"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment(self):
        """Non-logged-in users should get redirected to login on equipment view"""
        response = self.client.get("/equipment/")

        self.assertRedirects(response, "/accounts/login/?next=/equipment/")

class EquipmentViewsInputsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username="testuser1@foo.bar", password="top_secret1"
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
            user=cls.user1, equipment=cls.equipment2, role="USER"
        )
        cls.equipmentuser3 = EquipmentUser.objects.create(
            user=cls.user1, equipment=cls.equipment3, role="ADMIN"
        )

        # Create groups and permissions
        ct = ContentType.objects.get_for_model(Equipment)
        cls.permissions = dict()
        cls.permissions["add"], _ = Permission.objects.get_or_create(
            codename="add_equipment", content_type=ct
        )
        cls.permissions["change"], _ = Permission.objects.get_or_create(
            codename="change_equipment", content_type=ct
        )
        cls.permissions["view"], _ = Permission.objects.get_or_create(
            codename="view_equipment", content_type=ct
        )
        cls.permissions["delete"], _ = Permission.objects.get_or_create(
            codename="delete_equipment", content_type=ct
        )

    def setUp(self):
        self.client = Client()

    def test_equipment_index_has_add_button_for_user_with_permission(self):
        """Equipment index page should have add button for user with permission"""
        self.user1.user_permissions.add(self.permissions["add"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        # This is enough since we only want to test if a link exists,
        # not that it's actually valid HTML or anything.
        expected_html = """
            <a href="/equipment/add/" role="button">
                Add new equipment
            </a>
        """

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_index_no_add_button_for_user_with_no_permission(self):
        """Equipment index page should not have add button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Add new equipment")

    def test_equipment_index_has_edit_button_for_user_with_admin_permission(self):
        """Equipment index page should have edit button for user with ADMIN permission"""
        self.user1.user_permissions.add(self.permissions["change"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)

        expected_html = f"""
            <a href="/equipment/{self.equipment3.id}/edit/" role="button">
                Edit
            </a>
        """
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_index_no_edit_button_for_user_with_no_permission(self):
        """Equipment index page should not have edit button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit")

    def test_equipment_index_has_delete_button_for_user_with_permission(self):
        """Equipment index page should have delete button for user with permission"""
        self.user1.user_permissions.add(self.permissions["delete"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        for equipment in Equipment.objects.all():
            expected_html = f"""
                <a href="/equipment/{equipment.id}/delete/" class="secondary" data-confirm>
                    Delete
                </a>
            """
            self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_index_no_delete_button_for_user_with_no_permission(self):
        """Equipment index page should not have edit button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/equipment/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete")
