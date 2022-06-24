# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from equipment.models import Equipment
from equipment.utils import fetch_users_equipment


@method_decorator(login_required, name="dispatch")
class DashboardView(View):
    template_name = "dashboard/index.html"

    def get(self, request):
        data = {
            "equipment": fetch_users_equipment(request.user)
        }
        return render(request, self.template_name, data)
