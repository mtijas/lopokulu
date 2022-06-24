# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser

class DashboardViewAuthTestCase(TestCase):
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

    def test_respond_with_200_for_url_dashboard(self):
        """Response 200 should be given on url /dashboard/ for logged in user"""
        self.client.login(username="testuser1@foo.bar", password="top_secret1")

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_dashboard(self):
        """Non-logged-in users should get redirected to login on dashboard view"""
        response = self.client.get("/dashboard/")

        self.assertRedirects(response, "/accounts/login/?next=/dashboard/")
