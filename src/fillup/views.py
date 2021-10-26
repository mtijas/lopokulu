# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import FillupForm
from django.contrib.auth.decorators import login_required
from manager.models import Vehicle


@login_required
def add_fillup(request):
    if request.method == 'POST':
        form = FillupForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            return HttpResponseRedirect('/thanks/')

    else:
        form = FillupForm()

    form.fields['vehicle'].widget.choices.queryset = Vehicle.objects.filter(
        vehicleuser__person_id=request.user.id,
        vehicleuser__role__in=['DR', 'OW']
    )


    content = {
        'form': form,
    }
    return render(request, 'fillup/add_fillup.html', content)
