# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.urls import path

from equipment.views import (
    EquipmentAddView,
    EquipmentDeleteView,
    EquipmentDetailView,
    EquipmentEditView,
    EquipmentListView,
)

app_name = "equipment"
urlpatterns = [
    path("", EquipmentListView.as_view(), name="index"),
    path("<int:pk>/", EquipmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", EquipmentEditView.as_view(), name="edit"),
    path("<int:pk>/delete/", EquipmentDeleteView.as_view(), name="delete"),
    path("add/", EquipmentAddView.as_view(), name="add"),
]
