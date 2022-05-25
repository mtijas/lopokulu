# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView
from django.views import View

from equipment.models import Equipment, EquipmentUser
from equipment.forms import EquipmentForm


@method_decorator(login_required, name='dispatch')
class EquipmentListView(ListView):
    model = Equipment
    template_name = 'equipment/index.html'


@method_decorator(login_required, name='dispatch')
class EquipmentDetailView(DetailView):
    model = Equipment
    template_name = 'equipment/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = EquipmentUser.objects.filter(equipment=context['equipment'])
        context['roles'] = EquipmentUser.Role
        return context

@method_decorator(login_required, name='dispatch')
class EquipmentAddView(View):
    model = Equipment
    template_name = 'equipment/add.html'

    def get(self, request):
        form = EquipmentForm(request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = EquipmentForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment:index')

        return render(request, self.template_name, {'form': form})
