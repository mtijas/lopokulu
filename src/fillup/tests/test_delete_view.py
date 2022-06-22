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


class FillupDeleteViewAuthTestCase(TestCase):
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
        cls.fillup = Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment,
            addition_date=datetime.fromisoformat("2022-06-15T00:00:00+00:00"),
        )

    def setUp(self):
        self.client = Client()

    def test_redirects_non_logged_in_redirect_login_on_delete_fillup(self):
        """Non-logged-in users should get redirected to login on delete fillup view"""
        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertRedirects(response, f"/accounts/login/?next=/fillup/{self.fillup.id}/delete/")

    def test_nonauth_user_should_get_403(self):
        """Non-permissioned user should be given 403"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_403(self):
        """Read-only user should be given 403"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertEqual(response.status_code, 403)

    def test_user_user_should_get_302(self):
        """User-permissioned user should be given 302"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertEqual(response.status_code, 302)

    def test_admin_user_should_get_302(self):
        """Admin user should be given 302"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertEqual(response.status_code, 302)


class FillupViewsIntegrationTestCase(TestCase):
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
        cls.fillup1 = Fillup.objects.create(
            price=Decimal(1.8),
            amount=5,
            distance=100,
            equipment=cls.equipment3,
            tank_full=True,
            addition_date=datetime.fromisoformat("2022-06-15T15:00:00+00:00"),
        )
        cls.fillup2 = Fillup.objects.create(
            price=Decimal(1.9),
            amount=2,
            distance=200,
            equipment=cls.equipment3,
            tank_full=True,
            addition_date=datetime.fromisoformat("2022-06-15T16:00:00+00:00"),
        )
        cls.fillup3 = Fillup.objects.create(
            price=Decimal(1.9),
            amount=4,
            distance=250,
            equipment=cls.equipment3,
            tank_full=True,
            addition_date=datetime.fromisoformat("2022-06-15T17:00:00+00:00"),
        )

    def setUp(self):
        self.client = Client()

    def test_consumption_and_dist_delta_calculated_for_next_fillup_on_delete(self):
        """Consumption and distance delta should be calculated for next fillup on
        deleting fillup between two full fillups"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/{self.fillup2.id}/delete/")

        updated_fillup = Fillup.objects.get(pk=self.fillup3.id)

        self.assertRedirects(
            response, f"/fillup/equipment/{self.fillup2.equipment_id}/"
        )
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 150.0, places=1)
        self.assertAlmostEqual(float(updated_fillup.consumption), 2.667, places=3)

    def test_delete_actually_deletes(self):
        """GETting delete for existing fillup with credentials should actually delete"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/{self.fillup2.id}/delete/")

        self.assertTrue(Fillup.objects.filter(id=self.fillup1.id).exists())
        self.assertFalse(Fillup.objects.filter(id=self.fillup2.id).exists())
        self.assertTrue(Fillup.objects.filter(id=self.fillup3.id).exists())
