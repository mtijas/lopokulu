# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase

# Create your tests here.

class FailingTestCase(TestCase):
    def test_failing_for_jenkins_pipeline_development(self):
        self.assertTrue(False)
