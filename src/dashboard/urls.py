# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.urls import path

from dashboard.views import DashboardView

app_name = "dashboard"
urlpatterns = [
    path("", DashboardView.as_view(), name="index"),
]
