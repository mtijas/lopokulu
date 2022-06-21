# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2022 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.urls import path

from fillup.views import (
    FillupAddView,
    FillupDeleteView,
    FillupEditView,
    FillupEquipmentDetailView,
    FillupListView,
)

app_name = "fillup"
urlpatterns = [
    path("", FillupListView.as_view(), name="index"),
    path("equipment/<int:pk>/", FillupEquipmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", FillupEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", FillupDeleteView.as_view(), name="delete"),
    path("add/", FillupAddView.as_view(), name="add"),
    path(
        "add/equipment/<int:pk>/",
        FillupAddView.as_view(),
        name="add_fillup_for_equipment",
    ),
]
