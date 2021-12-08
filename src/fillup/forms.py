# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import forms
from .models import Fillup
from manager.models import Vehicle
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext as _


class FillupForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FillupForm, self).__init__(*args, **kwargs)
        self.fields['vehicle'].queryset = self.get_allowed_vehicles()
        self.fields['vehicle'].initial = self.fields['vehicle'].queryset[0].id

    def clean_distance(self):
        data = self.cleaned_data['distance']
        if data < 0:
            raise ValidationError(
                _('Distance should be zero or more'),
                code='invalid'
            )

        return data

    def clean(self):
        cleaned_data = super().clean()
        distance = cleaned_data.get('distance')
        vehicle = cleaned_data.get('vehicle')

        if vehicle is None:
            return

        # Get the latest fillup for vehicle in question
        previous_fillup = Fillup.objects.filter(
            vehicle_id=vehicle.id,
        ).first()

        if previous_fillup is None:
            return # It's ok to not have any fillups yet

        if distance <= previous_fillup.distance:
            self.add_error(
                'distance',
                _('Distance should be more than %(dist)s') % {'dist':previous_fillup.distance}
            )

    def get_allowed_vehicles(self):
        return Vehicle.objects.filter(
            vehicleuser__person_id=self.user.id,
            vehicleuser__role__in=['DR', 'OW']
        )

    class Meta:
        model = Fillup
        widgets = {'vehicle': forms.RadioSelect}
        fields = ['price', 'amount', 'distance', 'vehicle', 'tank_full']

    field_order = ['vehicle', 'distance', 'amount', 'price', 'tank_full']
