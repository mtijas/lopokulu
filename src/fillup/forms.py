# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import forms
from .models import Fillup
from manager.models import Vehicle
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class FillupForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FillupForm, self).__init__(*args, **kwargs)

    def clean_vehicle(self):
        data = self.cleaned_data['vehicle']
        if data not in self.get_allowed_vehicles():
            raise ValidationError(
                _("You are not allowed to report fillup for that vehicle"),
                code='invalid'
            )

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data

    def get_allowed_vehicles(self):
        return Vehicle.objects.filter(
            vehicleuser__person_id=self.user.id,
            vehicleuser__role__in=['DR', 'OW']
        )

    class Meta:
        model = Fillup
        fields = ['price', 'amount', 'distance', 'vehicle']
