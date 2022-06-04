# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import template

register = template.Library()


@register.simple_tag
def active(request, pattern):
    import re

    if re.search(f"^\/{pattern}", request.path):
        return "active"
    return ""


@register.filter
def get_dict_value(dictionary, key):
    return dictionary.get(key)


# @TODO: Unit test addstr
@register.filter
def addstr(arg1, arg2):
    return str(arg1) + str(arg2)
