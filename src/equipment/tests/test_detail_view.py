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

    def test_respond_with_200_for_url_equipment_correct_pk(self):
        """Response 200 should be given on url /equipment/1"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment(self):
        """Non-logged-in users should get redirected to login on equipment view"""
        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertRedirects(
            response, f"/accounts/login/?next=/equipment/{self.equipment1.id}/"
        )


class EquipmentViewsInputsTestCase(TestCase):
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

    def test_equipment_detail_has_edit_button_for_user_with_permission(self):
        """Equipment detail page should have edit button for user with permission"""
        self.user1.user_permissions.add(self.permissions["edit"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        expected_html = f"""
            <a href="/equipment/{self.equipment1.id}/edit/" role="button">
                Edit
            </a>
        """
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_detail_no_edit_button_for_user_with_no_permission(self):
        """Equipment detail page should not have edit button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Edit")

    def test_equipment_detail_has_delete_button_for_user_with_permission(self):
        """Equipment detail page should have delete button for user with permission"""
        self.user1.user_permissions.add(self.permissions["delete"])
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        expected_html = f"""
            <a href="/equipment/{self.equipment1.id}/delete/" class="secondary" data-confirm>
                Delete
            </a>
        """
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_detail_no_delete_button_for_user_with_no_permission(self):
        """Equipment detail page should not have edit button for user with no permission"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get(f"/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete")
