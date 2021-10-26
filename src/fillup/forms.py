# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import forms
from .models import Fillup


class FillupForm(forms.ModelForm):
    class Meta:
        model = Fillup
        fields = ['price', 'amount', 'distance', 'vehicle']
