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


class FillupViewsIntegrationTestCase(TestCase):
    def setUp(self):
        self.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        Vehicle.objects.create(name='TestRO', register_number='TEST-RO')
        Vehicle.objects.create(name='TestDR', register_number='TEST-DR')
        Vehicle.objects.create(name='TestOW', register_number='TEST-OW')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestRO'), role='RO')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestDR'), role='DR')
        VehicleUser.objects.create(
            person=self.user, vehicle=Vehicle.objects.get(name='TestOW'), role='OW')
        Fillup.objects.create(
            price=2.013,
            amount=42,
            distance=100,
            vehicle=Vehicle.objects.get(name='TestOW'),
        )
        self.client = Client()

    def test_respond_with_200_for_url_fillup(self):
        '''Response 200 should be given on url /fillup/'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)

    def test_respond_with_302_for_non_logged_in_on_fillup(self):
        '''Response 302 should be given to non-logged-in user on url /fillup/'''
        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 302)

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
