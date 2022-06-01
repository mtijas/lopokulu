# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.test import TestCase
from unittest.mock import Mock
from lopokulu.templatetags.lopokulu_extras import active



class TemplateTagsTestCase(TestCase):
    def test_active_returns_active_on_matching_pattern(self):
        '''Active should return 'active' when pattern found in request.path'''
        request = Mock()
        request.path = '/success/'
        pattern = 'success'

        result = active(request, pattern)

        self.assertEquals(result, 'active')

    def test_active_returns_active_on_matching_pattern_more_complex(self):
        '''Active should return 'active' when pattern found in complex request.path'''
        request = Mock()
        request.path = '/success/this/is/more/complex/example/'
        pattern = 'success'

        result = active(request, pattern)

        self.assertEquals(result, 'active')

    def test_active_returns_empty_str_on_nonmatching_pattern(self):
        '''Active should return '' when pattern not found in request.path'''
        request = Mock()
        request.path = '/success/'
        pattern = 'nonmatching'

        result = active(request, pattern)

        self.assertEquals(result, '')

    def test_active_returns_empty_str_first_part_not_matching(self):
        '''Active should return '' when pattern not found in request.path'''
        request = Mock()
        request.path = '/should/not/success/'
        pattern = 'success'

        result = active(request, pattern)

        self.assertEquals(result, '')
