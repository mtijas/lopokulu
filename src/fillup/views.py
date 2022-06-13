# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from equipment.models import Equipment, EquipmentUser

from .forms import FillupForm
from .models import Fillup


@login_required
def add_fillup(request, pk=None):
    if request.method == "POST":
        form = FillupForm(request.user, request.POST)
        if form.is_valid():
            fillup = form.save(commit=False)
            fillup.user = request.user
            fillup.addition_date = timezone.now()
            fillup.save()
            return redirect("fillup:index")

    elif pk is not None:
        initial_data = {"equipment": pk}
        form = FillupForm(request.user, initial=initial_data)
    else:
        form = FillupForm(request.user)

    content = {
        "form": form,
    }
    return render(request, "fillup/add_fillup.html", content)


@login_required
def index(request):
    equipmentusers = EquipmentUser.objects.filter(
        user=request.user, equipment__allowed_measurements__contains="fillup"
    )
    equipment = []

    for single_eu in equipmentusers:
        equipment.append(
            {
                "equipment": single_eu.equipment,
                "role": single_eu.role,
                "fillups": Fillup.objects.filter(equipment=single_eu.equipment)[:10],
            }
        )

    content = {
        "fillup_allowed_roles": ["USER", "ADMIN"],
        "equipment": equipment,
    }

    return render(request, "fillup/index.html", content)


@login_required
def single_equipment(request, pk):
    equipmentusers = get_object_or_404(
        EquipmentUser, user=request.user, equipment__pk=pk
    )

    content = {
        "fillup_allowed_roles": ["USER", "ADMIN"],
        "equipment": get_object_or_404(Equipment, pk=pk),
        "fillups": Fillup.objects.filter(equipment__pk=pk),
        "role": equipmentusers.role,
    }

    return render(request, "fillup/single_equipment.html", content)
