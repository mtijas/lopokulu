# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView
from django.utils.decorators import method_decorator

from equipment.models import Equipment, EquipmentUser

from fillup.forms import FillupForm
from fillup.models import Fillup


@method_decorator(login_required, name="dispatch")
class FillupListView(ListView):
    model = Fillup
    template_name = "fillup/index.html"

    def get(self, request, **kwargs):
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

        return render(request, self.template_name, content)


@method_decorator(login_required, name="dispatch")
class FillupEquipmentDetailView(DetailView):
    model = Fillup
    template_name = "fillup/single_equipment.html"

    def get(self, request, **kwargs):
        equipmentusers = get_object_or_404(
            EquipmentUser, user=request.user, equipment__pk=kwargs.get("pk")
        )

        content = {
            "fillup_allowed_roles": ["USER", "ADMIN"],
            "equipment": get_object_or_404(Equipment, pk=kwargs.get("pk")),
            "fillups": Fillup.objects.filter(equipment__pk=kwargs.get("pk")),
            "role": equipmentusers.role,
        }

        return render(request, "fillup/single_equipment.html", content)


@method_decorator(login_required, name="dispatch")
class FillupAddView(View):
    model = Fillup
    template_name = "fillup/add.html"

    def get(self, request, **kwargs):
        if "equipment_id" in self.kwargs:
            initial_data = {"equipment": kwargs.get("pk")}
            form = FillupForm(request.user, initial=initial_data)
        else:
            form = FillupForm(request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request, **kwargs):
        form = FillupForm(request.user, request.POST)
        if form.is_valid():
            fillup = form.save(commit=False)
            fillup.user = request.user
            fillup.save()
            fillup.update_next_consumption()
            return redirect("fillup:detail", fillup.equipment.id)
        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class FillupEditView(View):
    model = Fillup
    template_name = "fillup/edit.html"

    def get(self, request, **kwargs):
        content = dict()
        content["fillup"] = Fillup.objects.get(id=kwargs.get("pk"))
        content["form"] = FillupForm(request.user, instance=content["fillup"])
        return render(request, self.template_name, content)

    def post(self, request, **kwargs):
        content = dict()
        content["fillup"] = Fillup.objects.get(id=kwargs.get("pk"))
        form = FillupForm(request.user, request.POST, instance=content["fillup"])
        content["form"] = form
        if form.is_valid():
            fillup = form.save(commit=False)
            fillup.user = request.user
            fillup.save()
            fillup.update_next_consumption()
            return redirect("fillup:detail", fillup.equipment.id)
        return render(request, self.template_name, content)
