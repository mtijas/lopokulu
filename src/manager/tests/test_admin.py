# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from manager.admin import UserCreationForm, UserChangeForm, PersonAdmin


class UserCreationFormTestCase(TestCase):
    def test_empty_password1_or_password2_not_allowed(self):
        '''Empty password1 or password2 should not be allowed'''
        data = {
            'password1': '',
            'password2': '',
        }

        form = UserCreationForm(data=data)

        # This is enough since we don't want to test Django's innards
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

    def test_non_matching_passwords_not_allowed(self):
        '''Non-matching passwords should not be allowed'''
        expected = {
            'password2': ["Passwords don't match"]
        }
        data = {
            'password1': 'topsecret',
            'password2': 'tercespot',
        }

        form = UserCreationForm(data=data)

        subset = {k:v for k, v in form.errors.items() if k in expected}
        self.assertDictEqual(subset, expected)

    def test_user_saved_with_email_and_password(self):
        '''User should be saved with email and passwords provided'''
        data = {
            'email': 'test@foo.bar',
            'password1': 'topsecret',
            'password2': 'topsecret',
        }

        form = UserCreationForm(data=data)
        user = form.save()

        # Testing for email is enough since anything more would be testing
        # side effects actually. Those are tested elsewhere.
        self.assertEqual(data['email'], user.email)

    def test_user_saved_with_email_and_password_without_commit(self):
        '''User should be saved with email and passwords provided, no commit'''
        data = {
            'email': 'test@foo.bar',
            'password1': 'topsecret',
            'password2': 'topsecret',
        }

        form = UserCreationForm(data=data)
        user = form.save(False)

        # Testing for email is enough since anything more would be testing
        # side effects actually. Those are tested elsewhere.
        self.assertEqual(data['email'], user.email)
