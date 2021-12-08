# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from manager.models import Person, Vehicle
from .forms import FillupForm
from .models import Fillup


@login_required
def add_fillup(request, pk=None):
    if request.method == 'POST':
        form = FillupForm(request.user, request.POST)
        if form.is_valid():
            fillup = form.save(commit=False)
            fillup.person = request.user
            fillup.addition_date = timezone.now()
            fillup.save()
            return redirect('dashboard')

    elif pk is not None:
        initial_data = {
            'vehicle': pk
        }
        form = FillupForm(request.user, initial=initial_data)
    else:
        form = FillupForm(request.user)

    content = {
        'form': form,
    }
    return render(request, 'fillup/add_fillup.html', content)

@login_required
def dashboard(request):
    user = Person.objects.get(email=request.user)
    vehicles = []

    for vehicle in user.vehicles.all():
        vehicles.append({
            'vehicle': vehicle,
            'fillups': Fillup.objects.filter(vehicle=vehicle)[:10],
        })

    content = {
        'allowed_fillups': user.vehicles.filter(vehicleuser__role__in=['DR', 'OW']),
        'vehicles': vehicles,
    }

    return render(request, 'fillup/dashboard.html', content)

@login_required
def vehicle(request):
    user = Person.objects.get(email=request.user)
    vehicles = []

    for vehicle in user.vehicles.all():
        vehicles.append({
            'vehicle': vehicle,
        })

    content = {
        'allowed_fillups': user.vehicles.filter(vehicleuser__role__in=['DR', 'OW']),
        'vehicles': vehicles,
    }

    return render(request, 'fillup/vehicle.html', content)

@login_required
def single_vehicle(request, pk):
    user = Person.objects.get(email=request.user)

    content = {
        'allowed_fillups': user.vehicles.filter(vehicleuser__role__in=['DR', 'OW']),
        'vehicle': get_object_or_404(Vehicle, pk=pk),
        'fillups': Fillup.objects.filter(vehicle__pk=pk),
    }

    return render(request, 'fillup/single_vehicle.html', content)
