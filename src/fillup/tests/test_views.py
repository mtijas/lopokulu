# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from django.test import Client
from fillup.forms import FillupForm
from fillup.models import Fillup
from manager.models import Person, Vehicle, VehicleUser
from decimal import Decimal


class FillupViewsIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        cls.vehicle1 = Vehicle.objects.create(name='TestRO', register_number='TEST-RO')
        cls.vehicle2 = Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        cls.vehicle3 = Vehicle.objects.create(name='TestOW', register_number='TEST-OW')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle1, role='RO')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle2, role='DR')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle3, role='OW')
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            vehicle=cls.vehicle3,
        )

    def setUp(self):
        self.client = Client()

    def test_respond_with_200_for_url_fillup(self):
        '''Response 200 should be given on url /fillup/'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_fillup(self):
        '''Non-logged-in users should get redirected to login on fillup view'''
        response = self.client.get('/fillup/')

        self.assertRedirects(response, '/accounts/login/?next=/fillup/')

    def test_redirect_to_dashboard_after_successful_addition(self):
        '''User should be redirected to dashboard after successful fillup addition'''
        data = {
            'price': 1,
            'amount': 1,
            'distance': 101,
            'vehicle': Vehicle.objects.get(name='TestOW').id,
        }
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.post('/fillup/', data=data)

        self.assertRedirects(response, '/dashboard/')

    def test_returned_to_fillupform_on_invalid_data(self):
        '''User should be returned to add_fillup view on posting invalid data'''
        data = {}
        self.client.login(email='testuser@foo.bar', password='top_secret')

        with self.assertTemplateUsed('fillup/add_fillup.html'):
            response = self.client.post('/fillup/', data=data)

        self.assertEqual(response.status_code, 200)

    def test_respond_with_200_for_url_fillup_correct_pk(self):
        '''Response 200 should be given on url /fillup/1'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get('/fillup/1/')

        self.assertEqual(response.status_code, 200)

    def test_vehicle_is_preselected_on_existing_vehicle_id(self):
        '''Vehicle should be preselected on url /fillup/<id>'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'''<div id="id_vehicle">
                    <div><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0" checked>
                        {str(self.vehicle2)}</label>
                    </div>
                    <div><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1">
                        {str(self.vehicle3)}</label>
                    </div>
                </div>
            '''
        )

        response = self.client.get(f'/fillup/{self.vehicle2.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_vehicle_is_preselected_on_existing_vehicle_id_test_2(self):
        '''Vehicle should be preselected on url /fillup/<id>, test 2'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'''<div id="id_vehicle">
                    <div><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0">
                        {str(self.vehicle2)}</label>
                    </div>
                    <div><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1" checked>
                        {str(self.vehicle3)}</label>
                    </div>
                </div>
            '''
        )

        response = self.client.get(f'/fillup/{self.vehicle3.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_vehicle_is_preselected_by_default(self):
        '''Vehicle should be preselected on url /fillup/'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'''<div id="id_vehicle">
                    <div><label for="id_vehicle_0">
                        <input type="radio" name="vehicle" value="{self.vehicle2.id}" required id="id_vehicle_0" checked>
                        {str(self.vehicle2)}</label>
                    </div>
                    <div><label for="id_vehicle_1">
                        <input type="radio" name="vehicle" value="{self.vehicle3.id}" required id="id_vehicle_1">
                        {str(self.vehicle3)}</label>
                    </div>
                </div>
            '''
        )

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)


class DashboardViewsIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        cls.vehicle1 = Vehicle.objects.create(name='TestRO', register_number='TEST-RO')
        cls.vehicle2 = Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        cls.vehicle3 = Vehicle.objects.create(name='TestOW', register_number='TEST-OW')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle1, role='RO')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle2, role='DR')
        VehicleUser.objects.create(
            person=cls.user, vehicle=cls.vehicle3, role='OW')
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            vehicle=cls.vehicle3,
        )

    def setUp(self):
        self.client = Client()

    def test_redirects_to_login_for_non_logged_in_user_on_dashboard(self):
        '''Non-logged-in users should get redirected to login on dashboard view'''
        response = self.client.get('/dashboard/')

        self.assertRedirects(response, '/accounts/login/?next=/dashboard/')

    def test_vehicle_has_add_fillup_btn_for_owner(self):
        '''Vehicle should have add fillup button for owner'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/{self.vehicle3.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_vehicle_has_add_fillup_btn_for_driver(self):
        '''Vehicle should have add fillup button for driver'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/{self.vehicle2.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_vehicle_does_not_have_add_fillup_btn_for_readonly(self):
        '''Vehicle should have add fillup button for driver'''
        self.client.login(email='testuser@foo.bar', password='top_secret')
        needle = (
            f'<a href="/fillup/{self.vehicle1.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)
