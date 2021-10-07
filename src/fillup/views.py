# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import FillupForm
from django.contrib.auth.decorators import login_required


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

    return render(request, 'fillup/add_fillup.html', {'form': form})
