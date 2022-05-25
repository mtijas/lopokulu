# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from django.test import Client
#from equipment.forms import EquipmentForm
from equipment.models import Equipment, EquipmentUser
from manager.models import Person


class EquipmentViewsIntegrationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = Person.objects.create_user(email='testuser@foo.bar', password='top_secret')
        cls.equipment1 = Equipment.objects.create(name='TestRO', register_number='TEST-RO')
        cls.equipment2 = Equipment.objects.create(name='TestUSER', register_number='TEST-USER')
        cls.equipment3 = Equipment.objects.create(name='TestADMIN', register_number='TEST-ADMIN')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment1, role='READONLY')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment2, role='USER')
        EquipmentUser.objects.create(
            person=cls.user, equipment=cls.equipment3, role='ADMIN')

    def setUp(self):
        self.client = Client()

    def test_respond_with_200_for_url_equipment(self):
        '''Response 200 should be given on url /equipment/'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get('/equipment/')

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment(self):
        '''Non-logged-in users should get redirected to login on equipment view'''
        response = self.client.get('/equipment/')

        self.assertRedirects(response, '/accounts/login/?next=/equipment/')

    def test_respond_with_200_for_url_equipment_correct_pk(self):
        '''Response 200 should be given on url /equipment/1'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get(f'/equipment/{self.equipment1.id}/')

        self.assertEqual(response.status_code, 200)

    def test_equipment_index_has_add_button(self):
        '''Equipment index page should have button for adding new equipment'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        # This is enough since we only want to test if a link exists,
        # not that it's actually valid HTML or anything.
        expected_html = ('''
            <a href="/equipment/add/" role="button">
                Add new equipment
            </a>
        ''')

        response = self.client.get('/equipment/')

        self.assertEqual(response.status_code, 200)
        self.assertInHTML(expected_html, response.content.decode(), 1)

    def test_respond_with_200_for_get_equipment_add(self):
        '''Response 200 should be given on get /equipment/add/'''
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.get('/equipment/add/')

        self.assertEqual(response.status_code, 200)

    def test_redirects_to_login_for_non_logged_in_user_on_equipment_add(self):
        '''Non-logged-in users should get redirected to login on equipment/add view'''
        response = self.client.get('/equipment/add/')

        self.assertRedirects(response, '/accounts/login/?next=/equipment/add/')

    def test_redirect_to_equipment_main_view_after_successful_addition(self):
        '''User should be redirected to Equipment main view after successful equipment addition'''
        data = {
            'name': 'Test Equipment',
            'register_number': 'TEST-EQ1',
        }
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.post('/equipment/add/', data=data)

        self.assertRedirects(response, '/equipment/')

    def test_returned_to_equipmentform_on_invalid_data(self):
        '''User should be returned to add_equipment view on posting invalid data'''
        data = {}
        self.client.login(email='testuser@foo.bar', password='top_secret')

        response = self.client.post('/equipment/add/', data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'equipment/add.html')
