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


class FillupViewsAuthTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser@foo.bar", password="top_secret"
        )
        cls.equipment1 = Equipment.objects.create(
            name="TestADMIN",
            register_number="TEST-ADMIN",
            allowed_measurements=["fillup"],
        )
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role="ADMIN"
        )
        cls.fillup = Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment1,
            addition_date=datetime.fromisoformat("2022-06-15T00:00:00+00:00"),
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
        response = self.client.get(f"/fillup/add/equipment/{self.equipment1.id}/")

        self.assertRedirects(
            response,
            f"/accounts/login/?next=/fillup/add/equipment/{self.equipment1.id}/",
        )

    def test_logged_in_user_should_be_able_to_see_edit_form(self):
        """Response 200 should be given on url /edit/"""
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.get(f"/fillup/{self.fillup.id}/edit/")

        self.assertEqual(response.status_code, 200)

    def test_redirects_non_logged_in_redirect_login_on_add_fillup(self):
        """Non-logged-in users should get redirected to login on add fillup view"""
        response = self.client.get(f"/fillup/{self.fillup.id}/edit/")

        self.assertRedirects(
            response, f"/accounts/login/?next=/fillup/{self.fillup.id}/edit/"
        )

    def test_redirects_non_logged_in_redirect_login_on_delete_fillup(self):
        """Non-logged-in users should get redirected to login on delete fillup view"""
        response = self.client.get(f"/fillup/{self.fillup.id}/delete/")

        self.assertRedirects(response, f"/accounts/login/?next=/fillup/{self.fillup.id}/delete/")


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

        with self.assertTemplateUsed("fillup/add.html"):
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

    def test_equipment_has_add_fillup_btn_for_admin(self):
        """Equipment should have add fillup button for admin"""
        self.client.login(username="admin_user@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_has_add_fillup_btn_for_equipment_user(self):
        """Equipment should have add fillup button for equipment_user"""
        self.client.login(username="user_user@foo.bar", password="top_secret")
        expected_html = f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_does_not_have_add_fillup_btn_for_readonly(self):
        """Equipment should have add fillup button for equipment_user"""
        self.client.login(username="ro_user@foo.bar", password="top_secret")
        needle = f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'

        response = self.client.get("/fillup/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)

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

    def test_edit_form_gets_prepopulated(self):
        """Edit form should get pre-populated"""
        expected_equipment = f'<input type="radio" name="equipment" value="{self.equipment3.id}" required id="id_equipment_0" checked>'
        formatted_dt = timezone.localtime(self.fillup3.addition_date).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        expected_addition_date = f'value="{formatted_dt}"'
        expected_tank_full = (
            '<input type="checkbox" name="tank_full" id="id_tank_full" checked>'
        )

        self.client.login(username="testuser@foo.bar", password="top_secret")
        response = self.client.get(f"/fillup/{self.fillup3.id}/edit/")

        self.assertInHTML(expected_equipment, response.content.decode(), 1)
        self.assertInHTML(expected_tank_full, response.content.decode(), 1)
        self.assertIn(expected_addition_date, response.content.decode())
        self.assertIn("4.0", response.content.decode())
        self.assertIn("250.0", response.content.decode())
        self.assertIn("1.900", response.content.decode())

    def test_consumption_and_dist_delta_calculated_for_edited_fillup(self):
        """Consumption and distance delta should be calculated for edited fillup on
        editing fillup between two full fillups"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 220,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T16:00:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post(f"/fillup/{self.fillup2.id}/edit/", data=data)

        updated_fillup = Fillup.objects.get(pk=self.fillup2.id)

        self.assertAlmostEqual(float(updated_fillup.consumption), 3.25, places=3)
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 120.0, places=1)

    def test_consumption_and_dist_delta_calculated_for_edited_fillup_date_forward(self):
        """Consumption and distance delta should be calculated for edited fillup on
        editing fillup between two full fillups when addition_date moves forward"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 220,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T16:30:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post(
            f"/fillup/{self.fillup2.id}/edit/", data=data
        )

        updated_fillup = Fillup.objects.get(pk=self.fillup2.id)

        self.assertRedirects(response, f"/fillup/equipment/{updated_fillup.equipment_id}/")
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 120.0, places=1)
        self.assertAlmostEqual(float(updated_fillup.consumption), 3.25, places=3)

    def test_consumption_and_dist_delta_calculated_for_edited_fillup_date_backward(
        self,
    ):
        """Consumption and distance delta should be calculated for edited fillup on
        editing fillup between two full fillups when addition_date moves backward"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 220,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T15:30:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post(
            f"/fillup/{self.fillup2.id}/edit/", data=data
        )

        updated_fillup = Fillup.objects.get(pk=self.fillup2.id)

        self.assertRedirects(response, f"/fillup/equipment/{updated_fillup.equipment_id}/")
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 120.0, places=1)
        self.assertAlmostEqual(float(updated_fillup.consumption), 3.25, places=3)

    def test_consumption_and_dist_delta_calculated_for_next_fillup_on_edit(self):
        """Consumption and distance delta should be calculated for next fillup on
        editing fillup between two full fillups"""
        data = {
            "price": 1.8,
            "amount": 3.9,
            "distance": 220,
            "equipment": self.equipment3.id,
            "addition_date": "2022-06-15T15:30:00+00:00",
            "tank_full": "1",
        }
        self.client.login(username="testuser@foo.bar", password="top_secret")

        response = self.client.post(
            f"/fillup/{self.fillup2.id}/edit/", data=data
        )

        updated_fillup = Fillup.objects.get(pk=self.fillup3.id)

        self.assertRedirects(response, f"/fillup/equipment/{updated_fillup.equipment_id}/")
        self.assertAlmostEqual(float(updated_fillup.distance_delta), 30.0, places=1)
        self.assertAlmostEqual(float(updated_fillup.consumption), 13.333, places=3)
