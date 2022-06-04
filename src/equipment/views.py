# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import DetailView, ListView

from equipment.forms import EquipmentForm
from equipment.models import Equipment, EquipmentUser


@method_decorator(login_required, name="dispatch")
class EquipmentListView(ListView):
    model = Equipment
    template_name = "equipment/index.html"


@method_decorator(login_required, name="dispatch")
class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = "equipment/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["equipment_users"] = EquipmentUser.objects.filter(
            equipment=context["equipment"]
        )
        context["roles"] = EquipmentUser.Role
        return context


@method_decorator(login_required, name="dispatch")
class EquipmentAddView(PermissionRequiredMixin, View):
    model = Equipment
    template_name = "equipment/add.html"
    permission_required = "equipment.add_equipment"

    def get(self, request, **kwargs):
        content = dict()
        content["form"] = EquipmentForm(request.user)
        content["users"] = User.objects.all()
        content["roles"] = EquipmentUser.Role

        return render(request, self.template_name, content)

    def post(self, request, **kwargs):
        form = EquipmentForm(request.user, request.POST)

        if form.is_valid():
            saved_equipment = form.save()
            update_measurement_roles(request, saved_equipment)

            return redirect("equipment:detail", saved_equipment.id)

        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class EquipmentEditView(PermissionRequiredMixin, View):
    model = Equipment
    template_name = "equipment/edit.html"
    permission_required = "equipment.edit_equipment"

    def get(self, request, **kwargs):
        content = dict()
        content["equipment"] = Equipment.objects.get(id=kwargs.get("pk"))
        content["form"] = EquipmentForm(request.user, instance=content["equipment"])
        content["users"] = User.objects.all()
        content["roles"] = EquipmentUser.Role
        equipment_users = EquipmentUser.objects.filter(equipment=content["equipment"])
        content["equipment_users"] = dict()
        for eu in equipment_users:
            content["equipment_users"][eu.user.id] = eu.role

        return render(request, self.template_name, content)

    def post(self, request, **kwargs):
        content = dict()
        content["equipment"] = Equipment.objects.get(id=kwargs.get("pk"))
        form = EquipmentForm(request.user, request.POST, instance=content["equipment"])

        if form.is_valid():
            saved_equipment = form.save()
            update_measurement_roles(request, saved_equipment)

            return redirect("equipment:detail", saved_equipment.id)

        content["users"] = User.objects.all()
        content["roles"] = EquipmentUser.Role
        content["equipment_users"] = EquipmentUser.objects.filter(
            equipment=content["equipment"]
        )

        return render(request, self.template_name, {"form": form})


@method_decorator(login_required, name="dispatch")
class EquipmentDeleteView(PermissionRequiredMixin, View):
    model = Equipment
    permission_required = "equipment.delete_equipment"

    def get(self, request, **kwargs):
        Equipment.objects.get(id=kwargs.get("pk")).delete()
        return redirect("equipment:index")


def update_measurement_roles(request, equipment):
    # Clear old permissions as we will write them all for current Equipment
    EquipmentUser.objects.filter(equipment=equipment).delete()

    one_admin_created = False
    all_users = User.objects.all()
    for user in all_users:
        input_field_name = f"perm-{user.id}"
        if input_field_name not in request.POST:
            continue

        if request.POST[input_field_name] not in EquipmentUser.Role.names:
            continue

        EquipmentUser.objects.create(
            user=user,
            equipment=equipment,
            role=EquipmentUser.Role[request.POST[input_field_name]],
        )

        # Only admins may change permissions, so at least one needed
        if not one_admin_created and request.POST[input_field_name] == "ADMIN":
            one_admin_created = True

    # Update current user to ADMIN of no other admins were assigned
    if not one_admin_created:
        # Delete any permissions for current user since they might
        # be lower than ADMIN (for current equipment of course).
        EquipmentUser.objects.filter(equipment=equipment, user=request.user).delete()
        EquipmentUser.objects.create(
            user=request.user, equipment=equipment, role=EquipmentUser.Role.ADMIN
        )
