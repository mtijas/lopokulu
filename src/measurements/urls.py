# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from django.urls import path

from measurements.views import (MeasurementAddView, MeasurementDeleteView,
                                MeasurementDetailView, MeasurementEditView,
                                MeasurementListView)

app_name = 'measurements'
urlpatterns = [
    path('', MeasurementListView.as_view(), name='index'),
    path('<int:pk>/', MeasurementDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', MeasurementEditView.as_view(), name='edit'),
    path('<int:pk>/delete/', MeasurementDeleteView.as_view(), name='delete'),
    path('add/', MeasurementAddView.as_view(), name='add'),
]
