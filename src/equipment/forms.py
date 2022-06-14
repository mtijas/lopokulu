# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django import forms
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from .models import Equipment

MEASUREMENT_CHOICES = []
for app in settings.INSTALLED_MEASUREMENT_APPS:
    MEASUREMENT_CHOICES.append((app, app))


class EquipmentForm(forms.ModelForm):
    allowed_measurements = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=MEASUREMENT_CHOICES,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EquipmentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Equipment
        fields = ["name", "register_number", "allowed_measurements"]

    field_order = ["name", "register_number"]
