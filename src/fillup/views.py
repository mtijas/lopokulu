# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from .forms import FillupForm
from django.contrib.auth.decorators import login_required
from manager.models import Vehicle
from manager.models import Person


@login_required
def add_fillup(request):
    if request.method == 'POST':
        form = FillupForm(request.user, request.POST)
        if form.is_valid():
            fillup = form.save(commit=False)
            fillup.person = request.user
            fillup.addition_date = timezone.now()
            fillup.save()
            return HttpResponseRedirect('/dashboard/')

    else:
        form = FillupForm(request.user)

    content = {
        'form': form,
    }
    return render(request, 'fillup/add_fillup.html', content)

@login_required
def dashboard(request):
    user = Person.objects.get(email=request.user)
    allowed_vehicles = Vehicle.objects.filter(
        vehicleuser__person_id=user.id,
        vehicleuser__role__in=['DR', 'OW']
    )

    content = {
        'allowed_vehicles': allowed_vehicles
    }

    return render(request, 'fillup/dashboard.html', content)
