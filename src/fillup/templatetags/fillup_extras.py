# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import template

register = template.Library()

@register.simple_tag
def active(request, pattern):
    import re
    if re.search(f'^\/{pattern}', request.path):
        return 'active'
    return ''
