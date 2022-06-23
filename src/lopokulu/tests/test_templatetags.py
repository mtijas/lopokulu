# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from unittest.mock import Mock

from django.test import TestCase

from lopokulu.templatetags import lopokulu_extras


class TemplateTagsTestCase(TestCase):
    def test_active_returns_active_on_matching_pattern(self):
        """Active should return 'active' when pattern found in request.path"""
        request = Mock()
        request.path = "/success/"
        pattern = "success"

        result = lopokulu_extras.active(request, pattern)

        self.assertEquals(result, "active")

    def test_active_returns_active_on_matching_pattern_more_complex(self):
        """Active should return 'active' when pattern found in complex request.path"""
        request = Mock()
        request.path = "/success/this/is/more/complex/example/"
        pattern = "success"

        result = lopokulu_extras.active(request, pattern)

        self.assertEquals(result, "active")

    def test_active_returns_empty_str_on_nonmatching_pattern(self):
        """Active should return '' when pattern not found in request.path"""
        request = Mock()
        request.path = "/success/"
        pattern = "nonmatching"

        result = lopokulu_extras.active(request, pattern)

        self.assertEquals(result, "")

    def test_active_returns_empty_str_first_part_not_matching(self):
        """Active should return '' when pattern not found in request.path"""
        request = Mock()
        request.path = "/should/not/success/"
        pattern = "success"

        result = lopokulu_extras.active(request, pattern)

        self.assertEquals(result, "")

    def test_addstr_concatenates_strings(self):
        """addstr templatetag should concatenate two strings"""
        input1 = "kissat"
        input2 = "koiria"
        expected = "kissatkoiria"

        result = lopokulu_extras.addstr(input1, input2)

        self.assertEquals(result, expected)

    def test_addstr_concatenates_strings_2(self):
        """addstr templatetag should concatenate two strings, test 2"""
        input1 = "kissat"
        input2 = "koiria"
        expected = "koiriakissat"

        result = lopokulu_extras.addstr(input2, input1)

        self.assertEquals(result, expected)

    def test_addstr_concatenates_ints(self):
        """addstr templatetag should concatenate two ints (and not sum them)"""
        input1 = 1
        input2 = 2
        expected = "12"

        result = lopokulu_extras.addstr(input1, input2)

        self.assertEquals(result, expected)
