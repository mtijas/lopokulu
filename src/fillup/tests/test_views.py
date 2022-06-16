# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser
from fillup.forms import FillupForm
from fillup.models import Fillup


class FillupViewsAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser@foo.bar", password="top_secret"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestRO", register_number="TEST-RO", allowed_measurements=["fillup"]
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role="READ_ONLY"
        )

    def setUp(self):
        self.client = Client()

    def test_logged_in_users_see_fillup(self):
        """Response 200 should be given on url /fillup/"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_fillup(self):
        """Non-logged-in users should get redirected to login on fillup view"""
        response = self.client.get("/fillup/")

        self.assertRedirects(response, "/accounts/login/?next=/fillup/")

    def test_logged_in_user_sees_single_equipment_fillup_view(self):
        """Response 200 should be given on url /equipment/<id>"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_specific_equipment(self):
        """Non-logged-in users should get redirected to login on equipment view"""
        response = self.client.get("/fillup/equipment/1/")

        self.assertRedirects(response, "/accounts/login/?next=/fillup/equipment/1/")

    def test_logged_in_user_should_be_able_to_see_add_new_form(self):
        """Response 200 should be given on url /add/"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/add/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_redirect_login_on_add_fillup(self):
        """Non-logged-in users should get redirected to login on add fillup view"""
        response = self.client.get("/fillup/add/")

        self.assertRedirects(response, "/accounts/login/?next=/fillup/add/")

    def test_logged_in_user_should_be_able_to_see_add_new_form_test_2(self):
        """Response 200 should be given on url /add/equipment/<id>"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/add/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_redirect_login_on_add_fillup_for_equipment(self):
        """Non-logged-in users should get redirected to login on add fillup for equipment view"""
        response = self.client.get("/fillup/add/equipment/1/")

        self.assertRedirects(response, "/accounts/login/?next=/fillup/add/equipment/1/")


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
            addition_date=datetime.fromisoformat("2022-06-15T00:00:00+02:00"),
        )

    def setUp(self):
        self.client = Client()

    def test_redirect_to_detail_after_successful_addition(self):
        """User should be redirected to fillups index after successful fillup addition"""
        data = {
            "price": 1,
            "amount": 1,
            "distance": 101,
            "addition_date": "2022-06-15 12:00:00",
            "equipment": self.equipment3.id,
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post("/fillup/add/", data=data, follow=True)

        self.assertContains(response, "15.6.22 12:00")

    def test_returned_to_fillupform_on_invalid_data(self):
        """User should be returned to add_fillup view on posting invalid data"""
        data = {}
        self.client.login(username="testuser@foo.bar", password="top_secret")

        with self.assertTemplateUsed("fillup/add_fillup.html"):
            response = self.client.post("/fillup/add/", data=data)

        self.assertEqual(response.status_code, 200)

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

    def test_equipment_without_allow_selection_not_listed(self):
        """Equipment without fillup in allowed_measurements list should not be listed"""
        equipment4 = Equipment.objects.create(
            name="TestNotFound",
            register_number="TEST-NOT-FOUND",
            allowed_measurements=[],
        )
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(str(self.equipment1), response.content.decode(), 1)
        self.assertIn(str(self.equipment2), response.content.decode(), 1)
        self.assertIn(str(self.equipment3), response.content.decode(), 1)
        self.assertNotIn(str(equipment4), response.content.decode(), 1)


class FillupViewsInputsTestCase(TestCase):
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
        )

    def setUp(self):
        self.client = Client()

    def test_equipment_has_add_fillup_btn_for_admin(self):
        """Equipment should have add fillup button for admin"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_has_add_fillup_btn_for_equipment_user(self):
        """Equipment should have add fillup button for equipment_user"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_does_not_have_add_fillup_btn_for_readonly(self):
        """Equipment should have add fillup button for equipment_user"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        needle = f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)

    def test_single_equipment_page_has_add_fillup_btn_for_admin(self):
        """Single equipment page should have add fillup button for admin"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment3.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_has_add_fillup_btn_for_equipment_user(self):
        """Single equipment page should have add fillup button for equipment_user"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment2.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_does_not_have_add_fillup_btn_for_readonly(self):
        """Single equipment page should have add fillup button for equipment_user"""
        self.client.login(username="testuser@foo.bar", password="top_secret")
        needle = f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'

        response = self.client.get(f"/fillup/equipment/{self.equipment1.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)


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
            addition_date=datetime.fromisoformat("2022-06-15T15:00:00+02:00"),
        )
        cls.fillup2 = Fillup.objects.create(
            price=Decimal(1.9),
            amount=2,
            distance=200,
            equipment=cls.equipment3,
            tank_full=True,
            addition_date=datetime.fromisoformat("2022-06-15T16:00:00+02:00"),
        )
        cls.fillup3 = Fillup.objects.create(
            price=Decimal(1.9),
            amount=4,
            distance=250,
            equipment=cls.equipment3,
            tank_full=True,
            addition_date=datetime.fromisoformat("2022-06-15T17:00:00+02:00"),
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
            "addition_date": "2022-06-15T15:30:00+02:00",
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
            "addition_date": "2022-06-15T15:30:00+02:00",
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
