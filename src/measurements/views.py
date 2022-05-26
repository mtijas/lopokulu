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

#from measurements.forms import MeasurementForm
from measurements.models import Measurement


@method_decorator(login_required, name='dispatch')
class MeasurementListView(ListView):
    model = Measurement
    template_name = 'measurements/index.html'


@method_decorator(login_required, name='dispatch')
class MeasurementDetailView(DetailView):
    model = Measurement
    template_name = 'measurements/detail.html'


@method_decorator(login_required, name='dispatch')
class MeasurementAddView(PermissionRequiredMixin, View):
    model = Measurement
    template_name = 'measurements/add.html'
    permission_required = 'measurements.add_measurements'


@method_decorator(login_required, name='dispatch')
class MeasurementEditView(PermissionRequiredMixin, View):
    model = Measurement
    template_name = 'measurements/edit.html'
    permission_required = 'measurements.edit_measurements'


@method_decorator(login_required, name='dispatch')
class MeasurementDeleteView(PermissionRequiredMixin, View):
    model = Measurement
    permission_required = 'measurements.delete_measurements'
