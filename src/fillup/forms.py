# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils.translation import gettext as _

from equipment.models import Equipment

from .models import Fillup


class FillupForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FillupForm, self).__init__(*args, **kwargs)
        self.fields["equipment"].queryset = self.get_allowed_equipment()
        self.fields["equipment"].initial = self.fields["equipment"].queryset[0].id

    def clean_distance(self):
        data = self.cleaned_data["distance"]
        if data < 0:
            raise ValidationError(_("Distance should be zero or more"), code="invalid")

        return data

    def clean(self):
        cleaned_data = super().clean()
        distance = cleaned_data.get("distance")
        equipment = cleaned_data.get("equipment")
        addition_date = cleaned_data.get("addition_date")

        if "equipment" in self.errors or "addition_date" in self.errors:
            return

        # Get the previous fillup for equipment in question
        previous_fillup = Fillup.objects.filter(
            equipment=equipment, addition_date__lt=addition_date
        ).first()

        if distance is None:
            return

        if previous_fillup is not None:
            if distance <= previous_fillup.distance:
                self.add_error(
                    "distance",
                    _("Distance should be more than %(dist)s")
                    % {"dist": previous_fillup.distance},
                )

        # Get the next fillup for equipment in question
        next_fillup = Fillup.objects.filter(
            equipment=equipment, addition_date__gt=addition_date
        ).first()

        if next_fillup is not None:
            if distance >= next_fillup.distance:
                self.add_error(
                    "distance",
                    _("Distance should be less than %(dist)s")
                    % {"dist": next_fillup.distance},
                )

    def get_allowed_equipment(self):
        return Equipment.objects.filter(
            allowed_measurements__contains="fillup",
            equipmentuser__user_id=self.user.id,
            equipmentuser__role__in=["USER", "ADMIN"],
        )

    class Meta:
        model = Fillup
        widgets = {"equipment": forms.RadioSelect}
        fields = [
            "price",
            "amount",
            "distance",
            "equipment",
            "tank_full",
            "addition_date",
        ]

    field_order = [
        "equipment",
        "addition_date",
        "distance",
        "amount",
        "price",
        "tank_full",
    ]
