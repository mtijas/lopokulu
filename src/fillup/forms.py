# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.forms import ModelForm
from .models import Fillup


class FillupForm(ModelForm):
    class Meta:
        model = Fillup
        fields = ['price', 'amount', 'distance', 'vehicle']
