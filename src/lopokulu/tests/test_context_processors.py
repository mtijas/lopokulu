# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from unittest.mock import Mock

from django.conf import settings
from django.test import TestCase

from lopokulu import context_processors


class ContextProcessorsTestCase(TestCase):
    def test_measurement_apps_returned_as_dict(self):
        """Installed measurement apps should be returned as dict"""
        request = Mock()

        apps = context_processors.measurement_apps(request)

        self.assertTrue(isinstance(apps, dict))
        self.assertEqual(apps["MEASUREMENT_APPS"], settings.INSTALLED_MEASUREMENT_APPS)
