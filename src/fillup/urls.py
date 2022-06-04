# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.urls import path

from . import views

app_name = "fillup"
urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add_fillup, name="add_fillup"),
    path("add/equipment/<int:pk>/", views.add_fillup, name="add_fillup_for_equipment"),
    path("equipment/<int:pk>/", views.single_equipment, name="single_equipment"),
]
