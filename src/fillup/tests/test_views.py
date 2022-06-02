# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import Client, TestCase

from equipment.models import Equipment, EquipmentUser
from fillup.forms import FillupForm
from fillup.models import Fillup


class FillupViewsBasicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser@foo.bar', password='top_secret')
        cls.equipment1 = Equipment.objects.create(name='TestRO', register_number='TEST-RO')
        cls.equipment2 = Equipment.objects.create(name='TestUSER', register_number='TEST-USER')
        cls.equipment3 = Equipment.objects.create(name='TestADMIN', register_number='TEST-ADMIN')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role='READ_ONLY')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment2, role='USER')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment3, role='ADMIN')
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment3,
        )

    def setUp(self):
        self.client = Client()

    def test_respond_with_200_for_url_fillup(self):
        '''Response 200 should be given on url /fillup/'''
        self.client.login(username='testuser@foo.bar', password='top_secret')

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_fillup(self):
        '''Non-logged-in users should get redirected to login on fillup view'''
        response = self.client.get('/fillup/')

        self.assertRedirects(response, '/accounts/login/?next=/fillup/')

    def test_redirect_to_index_after_successful_addition(self):
        '''User should be redirected to fillups index after successful fillup addition'''
        data = {
            'price': 1,
            'amount': 1,
            'distance': 101,
            'equipment': Equipment.objects.get(name='TestADMIN').id,
        }
        self.client.login(username='testuser@foo.bar', password='top_secret')

        response = self.client.post('/fillup/add/', data=data)

        self.assertRedirects(response, '/fillup/')

    def test_returned_to_fillupform_on_invalid_data(self):
        '''User should be returned to add_fillup view on posting invalid data'''
        data = {}
        self.client.login(username='testuser@foo.bar', password='top_secret')

        with self.assertTemplateUsed('fillup/add_fillup.html'):
            response = self.client.post('/fillup/add/', data=data)

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_specific_equipment(self):
        '''Non-logged-in users should get redirected to login on equipment view'''
        response = self.client.get('/fillup/equipment/1/')

        self.assertRedirects(response, '/accounts/login/?next=/fillup/equipment/1/')

    def test_respond_with_200_for_url_equipment_single(self):
        '''Response 200 should be given on url /equipment/<id>'''
        self.client.login(username='testuser@foo.bar', password='top_secret')

        response = self.client.get(f'/fillup/equipment/{self.equipment1.id}/')

        self.assertEqual(response.status_code, 200)

    def test_return_404_on_incorrect_equipment_id(self):
        '''404 should be returned to user on missing equipment'''
        self.client.login(username='testuser@foo.bar', password='top_secret')

        response = self.client.get('/fillup/equipment/9999/')

        self.assertEqual(response.status_code, 404)

    def test_fillups_listed_on_single_equipment_page(self):
        '''Single equipment page should have fillups listed when there are any'''
        self.client.login(username='testuser@foo.bar', password='top_secret')

        response = self.client.get(f'/fillup/equipment/{self.equipment3.id}/')

        self.assertNotContains(response, 'No results...')

    def test_no_fillups_listed_on_single_equipment_page_when_empty(self):
        '''Single equipment page should not have fillups listed when there aren't any'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        needle = 'No results...'

        response = self.client.get(f'/fillup/equipment/{self.equipment1.id}/')

        self.assertContains(response, needle)


class FillupViewsInputsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser@foo.bar', password='top_secret')
        cls.equipment1 = Equipment.objects.create(name='TestRO', register_number='TEST-RO')
        cls.equipment2 = Equipment.objects.create(name='TestUSER', register_number='TEST-USER')
        cls.equipment3 = Equipment.objects.create(name='TestADMIN', register_number='TEST-ADMIN')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment1, role='READ_ONLY')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment2, role='USER')
        EquipmentUser.objects.create(
            user=cls.user, equipment=cls.equipment3, role='ADMIN')
        Fillup.objects.create(
            price=Decimal(2.013),
            amount=42,
            distance=100,
            equipment=cls.equipment3,
        )

    def setUp(self):
        self.client = Client()

    def test_equipment_has_add_fillup_btn_for_admin(self):
        '''Equipment should have add fillup button for admin'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_has_add_fillup_btn_for_equipment_user(self):
        '''Equipment should have add fillup button for equipment_user'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_equipment_does_not_have_add_fillup_btn_for_readonly(self):
        '''Equipment should have add fillup button for equipment_user'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        needle = (
            f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get('/fillup/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)

    def test_single_equipment_page_has_add_fillup_btn_for_admin(self):
        '''Single equipment page should have add fillup button for admin'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/add/equipment/{self.equipment3.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get(f'/fillup/equipment/{self.equipment3.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_has_add_fillup_btn_for_equipment_user(self):
        '''Single equipment page should have add fillup button for equipment_user'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        expected_html = (
            f'<a href="/fillup/add/equipment/{self.equipment2.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get(f'/fillup/equipment/{self.equipment2.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_single_equipment_page_does_not_have_add_fillup_btn_for_readonly(self):
        '''Single equipment page should have add fillup button for equipment_user'''
        self.client.login(username='testuser@foo.bar', password='top_secret')
        needle = (
            f'<a href="/fillup/add/equipment/{self.equipment1.id}/" role="button">Add fillup</a>'
        )

        response = self.client.get(f'/fillup/equipment/{self.equipment1.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(needle, response.content.decode(), 1)
