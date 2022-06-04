# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from django.conf import settings


class SettingsTestCase(TestCase):
    def test_measurement_apps_appended_to_installed_apps(self):
        '''Installed measurement apps should be added to installed apps array'''
        for app in settings.INSTALLED_MEASUREMENT_APPS:
            self.assertIn(app, settings.INSTALLED_APPS)

