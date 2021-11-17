# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from manager.models import PersonManager, Vehicle, Person, VehicleUser


class PersonTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Person.objects.create(email='person@foo.bar')
        Person.objects.create_staff(email='staff@foo.bar')
        Person.objects.create_superuser(email='superuser@foo.bar')

    def test_create_user_none_email_should_raise_value_error(self):
        '''ValueError should be raised when email is None'''
        person_manager = PersonManager()

        with self.assertRaises(ValueError):
            user = person_manager.create_user(None)

    def test_create_user_empty_email_should_raise_value_error(self):
        '''ValueError should be raised when email is empty'''
        person_manager = PersonManager()

        with self.assertRaises(ValueError):
            user = person_manager.create_user('')

    def test_created_user_should_be_active(self):
        '''Basic user should not be staff, admin or superuser'''
        person = Person.objects.get(email='person@foo.bar')

        self.assertTrue(person.is_active)

    def test_created_user_should_not_have_escalated_privileges(self):
        '''Basic user should not be staff, admin or superuser'''
        person = Person.objects.get(email='person@foo.bar')

        self.assertFalse(person.is_staff)
        self.assertFalse(person.is_admin)
        self.assertFalse(person.is_superuser)

    def test_created_staff_should_not_be_admin_or_superuser(self):
        '''Staff user should not be admin or superuser'''
        person = Person.objects.get(email='staff@foo.bar')

        self.assertTrue(person.is_staff)
        self.assertFalse(person.is_admin)
        self.assertFalse(person.is_superuser)

    def test_created_superuser_should_have_all_privileges(self):
        '''Superuser should have all privileges'''
        person = Person.objects.get(email='superuser@foo.bar')

        self.assertTrue(person.is_staff)
        self.assertTrue(person.is_admin)
        self.assertTrue(person.is_superuser)


class VehicleUserTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        vehicle = Vehicle.objects.create(register_number='TV-1', name='TEST VEHICLE')
        person = Person.objects.create(email='person@foo.bar')
        VehicleUser.objects.create(vehicle=vehicle, person=person)

    def test_default_role_is_RO(self):
        '''Default role should be RO when attaching Person to Vehicle'''
        vehicle = Vehicle.objects.get(register_number='TV-1')
        person = Person.objects.get(email='person@foo.bar')
        vehicle_user = VehicleUser.objects.get(vehicle=vehicle.id, person=person.id)

        self.assertEqual(vehicle_user.role, 'RO')

    def test_role_DR_is_assignable(self):
        '''VehicleUser should have role DR assignable'''
        vehicle = Vehicle.objects.get(register_number='TV-1')
        person = Person.objects.get(email='person@foo.bar')
        vehicle_user = VehicleUser.objects.create(
            vehicle=vehicle, person=person, role='DR')

        self.assertEqual(vehicle_user.role, 'DR')

    def test_role_OW_is_assignable(self):
        '''VehicleUser should have role OW assignable'''
        vehicle = Vehicle.objects.get(register_number='TV-1')
        person = Person.objects.get(email='person@foo.bar')
        vehicle_user = VehicleUser.objects.create(
            vehicle=vehicle, person=person, role='OW')

        self.assertEqual(vehicle_user.role, 'OW')

    def test_str_outputs_correctly(self):
        '''VehicleUser __str__ should output correctly'''
        vehicle = Vehicle.objects.get(register_number='TV-1')
        person = Person.objects.get(email='person@foo.bar')
        vehicle_user = VehicleUser.objects.get(vehicle=vehicle.id, person=person.id)
        expected = f'TEST VEHICLE has RO person {person}'

        self.assertEqual(str(vehicle_user), expected)
