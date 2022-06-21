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


class FillupAddViewAuthTestCase(TestCase):
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
        cls.equipment2 = Equipment.objects.create(
            name="TestEQ2",
            register_number="TEST-EQ2",
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
        cls.data = {
            "price": 1,
            "amount": 1,
            "distance": 101,
            "addition_date": "2022-06-15 12:00:00",
            "equipment": cls.equipment.id,
        }

    def setUp(self):
        self.client = Client()

    def test_redirects_non_logged_in_redirect_login_on_add_fillup(self):
        """Non-logged-in users should get redirected to login on add fillup view"""
        response = self.client.get("/fillup/add/")

        self.assertRedirects(response, "/accounts/login/?next=/fillup/add/")

    def test_nonauth_user_should_get_403(self):
        """Non-permissioned user should be given 403"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.get("/fillup/add/")

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_403(self):
        """Read-only user should be given 403"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.get("/fillup/add/")

        self.assertEqual(response.status_code, 403)

    def test_user_user_should_get_200(self):
        """User-permissioned user should be given 200"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.get("/fillup/add/")

        self.assertEqual(response.status_code, 200)

    def test_admin_user_should_get_200(self):
        """Admin user should be given 200"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.get("/fillup/add/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_redirect_login_on_add_fillup_for_equipment(self):
        """Non-logged-in users should get redirected to login on add fillup view"""
        response = self.client.get(f"/fillup/add/equipment/{self.equipment.id}/")

        self.assertRedirects(response, f"/accounts/login/?next=/fillup/add/equipment/{self.equipment.id}/")

    def test_nonauth_user_should_get_403_on_add_for_equipment(self):
        """Non-permissioned user should be given 403 on add fillup for equipment"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/add/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_403_on_add_for_equipment(self):
        """Read-only user should be given 403 on add fillup for equipment"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/add/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 403)

    def test_user_user_should_get_200_on_add_for_equipment(self):
        """User-permissioned user should be given 200 on add fillup for equipment"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/add/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 200)

    def test_admin_user_should_get_200_on_add_for_equipment(self):
        """Admin user should be given 200 on add fillup for equipment"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.get(f"/fillup/add/equipment/{self.equipment.id}/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_redirect_login_on_add_fillup_on_post(self):
        """Non-logged-in users should get redirected to login on add fillup view post"""
        response = self.client.post("/fillup/add/", data=self.data)

        self.assertRedirects(response, "/accounts/login/?next=/fillup/add/")

    def test_nonauth_user_should_get_403_on_post(self):
        """Non-permissioned user should be given 403 on post"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.post("/fillup/add/", data=self.data)

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_200_on_post(self):
        """Read-only user should be given 200 on post"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.post("/fillup/add/", data=self.data)

        self.assertEqual(response.status_code, 403)

    def test_user_user_should_get_200_on_post(self):
        """User-permissioned user should be given 200 on post"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.post("/fillup/add/", data=self.data)

        self.assertRedirects(response, f"/fillup/equipment/{self.data['equipment']}/")

    def test_admin_user_should_get_200_on_post(self):
        """Admin user should be given 200 on post"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.post("/fillup/add/", data=self.data)

        self.assertRedirects(response, f"/fillup/equipment/{self.data['equipment']}/")

    def test_redirects_non_logged_in_redirect_login_on_add_fillup_for_equipment_on_post(self):
        """Non-logged-in users should get redirected to login on add fillup view on post"""
        response = self.client.post(f"/fillup/add/equipment/{self.equipment.id}/", data=self.data)

        self.assertRedirects(response, f"/accounts/login/?next=/fillup/add/equipment/{self.equipment.id}/")

    def test_nonauth_user_should_get_403_on_add_for_equipment_on_post(self):
        """Non-permissioned user should be given 403 on add fillup for equipment on post"""
        self.client.login(
            username=self.nonauth_user.username, password="top_secret"
        )

        response = self.client.post(f"/fillup/add/equipment/{self.equipment.id}/", data=self.data)

        self.assertEqual(response.status_code, 403)

    def test_ro_user_should_get_403_on_add_for_equipment_on_post(self):
        """Read-only user should be given 403 on add fillup for equipment on post"""
        self.client.login(
            username=self.ro_user.username, password="top_secret"
        )

        response = self.client.post(f"/fillup/add/equipment/{self.equipment.id}/", data=self.data)

        self.assertEqual(response.status_code, 403)

    def test_user_user_should_be_redirected_on_add_for_equipment_on_post(self):
        """User-permissioned user should be given 200 on add fillup for equipment on post"""
        self.client.login(
            username=self.user_user.username, password="top_secret"
        )

        response = self.client.post(f"/fillup/add/equipment/{self.equipment.id}/", data=self.data)

        self.assertRedirects(response, f"/fillup/equipment/{self.data['equipment']}/")

    def test_admin_user_should_be_redirected_on_add_for_equipment_on_post(self):
        """Admin user should be given 200 on add fillup for equipment on post"""
        self.client.login(
            username=self.admin_user.username, password="top_secret"
        )

        response = self.client.post(f"/fillup/add/equipment/{self.equipment.id}/", data=self.data)

        self.assertRedirects(response, f"/fillup/equipment/{self.data['equipment']}/")


class FillupViewsBasicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser@foo.bar", password="top_secret"
        )
        cls.equipment = Equipment.objects.create(
            name="TestADMIN",
            register_number="TEST-ADMIN",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment, role="ADMIN"
        )

    def setUp(self):
        self.client = Client()

    def test_fillup_shows_on_detail_after_successful_addition(self):
        """Fillup should be shown on detail view after successful fillup addition"""
        data = {
            "price": 1,
            "amount": 1,
            "distance": 101,
            "addition_date": "2022-06-15 12:00:00",
            "equipment": self.equipment.id,
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post("/fillup/add/", data=data, follow=True)

        self.assertContains(response, "15.6.22 12:00")

    def test_returned_to_fillupform_on_invalid_data(self):
        """User should be returned to add_fillup view on posting invalid data"""
        data = {}
        self.client.login(username="testuser@foo.bar", password="top_secret")

        with self.assertTemplateUsed("fillup/add.html"):
            response = self.client.post("/fillup/add/", data=data)

        self.assertEqual(response.status_code, 200)


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

    def test_consumption_calculated_on_insert_between_existing_fillups(self):
        """Consumption should be calculated for new fillup on
        inserting new fillup between two full fillups"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 160,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T15:30:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post("/fillup/add/", data=data)

        updated_fillup = Fillup.objects.filter(
            distance=160, equipment=self.equipment3.id
        ).first()

        self.assertAlmostEqual(float(updated_fillup.consumption), 6.5, places=3)

    def test_consumption_and_dist_delta_calculated_for_next_fillup_on_insert(self):
        """Consumption and distance delta should be calculated for next fillup on
        inserting new fillup between two full fillups"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 160,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T15:30:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post("/fillup/add/", data=data)

        updated_fillup = Fillup.objects.filter(
            distance=200, equipment=self.equipment3.id
        ).first()

        self.assertAlmostEqual(float(self.fillup2.consumption), 2.0, places=3)
        self.assertAlmostEqual(float(self.fillup2.distance_delta), 100.0, places=1)
        self.assertAlmostEqual(float(updated_fillup.consumption), 5.0, places=3)
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 40.0, places=1)
