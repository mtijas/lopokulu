# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from .models import Equipment


class EquipmentForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EquipmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Equipment
        fields = ["name", "register_number"]

    field_order = ["name", "register_number"]
