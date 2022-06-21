# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase
from django.utils import timezone

from equipment.models import Equipment, EquipmentUser
from fillup.forms import FillupForm
from fillup.models import Fillup


class FillupEquipmentDetailViewAuthTestCase(TestCase):
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
        cls.equipment = Equipment.objects.create(
            name="TestEQ1",
            register_number="TEST-EQ1",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.ro_user, equipment=cls.equipment, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user_user, equipment=cls.equipment, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.admin_user, equipment=cls.equipment, role="ADMIN"
        )

    def setUp(self):
        self.client = Client()

    def test_redirects_non_logged_in(self):
        """Non-logged-in users should get redirected to login on list fillup view"""
        response = self.client.get(f"/fillup/equipment/{self.equipment.id}/")

        self.assertRedirects(response, f"/accounts/login/?next=/fillup/equipment/{self.equipment.id}/")

    def test_nonauth_user_should_get_403_on_list_for_equipment(self):
        """Non-permissioned user should be given 403 on list fillup for equipment"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_200_on_list_for_equipment(self):
        """Read-only user should be given 200 on list fillup for equipment"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 200)

    def test_user_user_should_get_200_on_list_for_equipment(self):
        """User-permissioned user should be given 200 on list fillup for equipment"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 200)

    def test_admin_user_should_get_200_on_list_for_equipment(self):
        """Admin user should be given 200 on list fillup for equipment"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 200)


class FillupViewsBasicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser@foo.bar", password="top_secret"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO", allowed_measurements=["fillup"]
        )
        cls.equipment2 = Equipment.objects.create(
            name="TestUSER",
            register_number="TEST-USER",
            allowed_measurements=["fillup"],
        )
        cls.equipment3 = Equipment.objects.create(
            name="TestADMIN",
            register_number="TEST-ADMIN",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment2, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment3, role="ADMIN"
        )
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment3,
            addition_date=datetime.fromisoformat("2022-06-15T00:00:00+00:00"),
        )

    def setUp(self):
        self.client = Client()

    def test_return_404_on_incorrect_equipment_id(self):
        """404 should be returned to user on missing equipment"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get("/fillup/equipment/9999/")

        self.assertEqual(response.status_code, 404)

    def test_fillups_listed_on_single_equipment_page(self):
        """Single equipment page should have fillups listed when there are any"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertNotContains(response, "No results...")

    def test_no_fillups_listed_on_single_equipment_page_when_empty(self):
        """Single equipment page should not have fillups listed when there aren't any"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        needle = "No results..."

        response = self.client.get(f"/fillup/equipment/{self.equipment1.id}/")

        self.assertContains(response, needle)


class FillupViewsInputsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user(
            username="admin_user@foo.bar", password="top_secret"
        )
        cls.ro_user = User.objects.create_user(
            username="ro_user@foo.bar", password="top_secret"
        )
        cls.user_user = User.objects.create_user(
            username="user_user@foo.bar", password="top_secret"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO", allowed_measurements=["fillup"]
        )
        cls.equipment2 = Equipment.objects.create(
            name="TestUSER",
            register_number="TEST-USER",
            allowed_measurements=["fillup"],
        )
        cls.equipment3 = Equipment.objects.create(
            name="TestADMIN",
            register_number="TEST-ADMIN",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.ro_user, equipment=cls.equipment1, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user_user, equipment=cls.equipment2, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.ro_user, equipment=cls.equipment3, role="READ_ONLY"
        )
        EquipmentUser.objects.create(
            user=cls.user_user, equipment=cls.equipment3, role="USER"
        )
        EquipmentUser.objects.create(
            user=cls.admin_user, equipment=cls.equipment3, role="ADMIN"
        )
        cls.fillups = list()
        cls.fillups.append(
            Fillup.objects.create(
                price=Decimal(2.013),
                amount=42,
                distance=100,
                equipment=cls.equipment3,
                user=cls.admin_user,
            )
        )
        cls.fillups.append(
            Fillup.objects.create(
                price=Decimal(2.013),
                amount=43,
                distance=200,
                equipment=cls.equipment3,
                user=cls.user_user,
            )
        )
        cls.fillups.append(
            Fillup.objects.create(
                price=Decimal(2.013),
                amount=44,
                distance=300,
                equipment=cls.equipment3,
                user=cls.admin_user,
            )
        )

    def setUp(self):
        self.client = Client()

    def test_single_equipment_page_has_add_fillup_btn_for_admin(self):
        """Single equipment page should have add fillup button for admin"""
        self.client.login(username="admin_user@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_has_add_fillup_btn_for_equipment_user(self):
        """Single equipment page should have add fillup button for equipment_user"""
        self.client.login(username="user_user@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment2.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_does_not_have_add_fillup_btn_for_readonly(self):
        """Single equipment page should have add fillup button for equipment_user"""
        self.client.login(username="ro_user@foo.bar", password="top_secret")
        needle = f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)

    def test_readonly_should_not_see_edit_fillup_buttons(self):
        """READ_ONLY user should not see edit fillup buttons"""
        self.client.login(username="ro_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/edit/" role="button">Edit</a>'
            self.assertNotIn(needle, response.content.decode(), 1)

    def test_useruser_should_see_edit_fillup_buttons_for_own_fillups(self):
        """USER user should see edit fillup buttons on their own fillups"""
        self.client.login(username="user_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/edit/" role="button">Edit</a>'
            if fillup.user_id == self.user_user.id:
                self.assertIn(needle, response.content.decode(), 1)
            else:
                self.assertNotIn(needle, response.content.decode(), 1)

    def test_admin_should_see_edit_fillup_buttons_for_all_fillups(self):
        """ADMIN user should see edit fillup buttons for all fillups"""
        self.client.login(username="admin_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/edit/" role="button">Edit</a>'
            self.assertIn(needle, response.content.decode(), 1)

    def test_readonly_should_not_see_delete_fillup_buttons(self):
        """READ_ONLY user should not see delete fillup buttons"""
        self.client.login(username="ro_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/delete/" class="secondary" data-confirm>Delete</a>'
            self.assertNotIn(needle, response.content.decode(), 1)

    def test_useruser_should_see_delete_fillup_buttons_for_own_fillups(self):
        """USER user should see delete fillup buttons on their own fillups"""
        self.client.login(username="user_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/delete/" class="secondary" data-confirm>Delete</a>'
            if fillup.user_id == self.user_user.id:
                self.assertIn(needle, response.content.decode(), 1)
            else:
                self.assertNotIn(needle, response.content.decode(), 1)

    def test_admin_should_see_delete_fillup_buttons_for_all_fillups(self):
        """ADMIN user should see delete fillup buttons for all fillups"""
        self.client.login(username="admin_user@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)

        for fillup in self.fillups:
            needle = f'<a href="/fillup/{fillup.id}/delete/" class="secondary" data-confirm>Delete</a>'
            self.assertIn(needle, response.content.decode(), 1)
