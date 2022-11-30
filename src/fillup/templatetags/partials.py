# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

import json

from datetime import timedelta

from django import template
from django.db.models import Avg, Sum
from django.utils.timezone import now

from fillup.models import Fillup

register = template.Library()


@register.inclusion_tag("fillup/tags/equipment_stats.html")
def fillup_equipment_stats(equipment, start_dt=92, stop_dt=None, mode: str = None):
    """Collects fillup stats for datetime range for specific equipment"""
    if stop_dt is None:
        stop_dt = now()

    if mode == "current year":
        start_dt = now().replace(day=1, month=1)
    elif type(start_dt) is int:
        start_dt = now() - timedelta(days=start_dt)

    data = {
        "equipment": equipment,
        "start_dt": start_dt,
        "stop_dt": stop_dt,
        "mode": mode,
        "chart": None,
        "stats": {
            "consumption__avg": 0,
            "total_price__sum": 0,
            "distance_delta__sum": 0,
        },
    }

    start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    stop_dt = stop_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    fillups = Fillup.objects.filter(
        addition_date__gte=start_dt, addition_date__lte=stop_dt, equipment=equipment
    ).order_by("addition_date")

    if not fillups:
        return data

    labels = []
    consumption_data = []
    price_data = []
    for fillup in fillups:
        labels.append(fillup.addition_date.strftime("%d.%-m."))
        consumption_data.append(fillup.consumption)
        price_data.append(str(fillup.price))

    data["chart"] = {
        "labels": json.dumps(labels),
        "datasets": json.dumps(
            [
                {
                    "label": "Consumption (l/100km)",
                    "data": consumption_data,
                    "fill": True,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgb(198, 235, 235, 0.25)",
                    "spanGaps": True,
                    "yAxisID": "y1"
                },
                {
                    "label": "Price (€/l)",
                    "data": price_data,
                    "fill": True,
                    "borderColor": "rgb(192, 75, 192)",
                    "backgroundColor": "rgb(235, 198, 235, 0.25)",
                    "spanGaps": True,
                    "yAxisID": "y2"
                },
            ]
        ),
        "options": json.dumps(
            {
                "scales": {
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "l/100km"
                        }
                    },
                    "y2": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "grid": {
                            "drawOnChartArea": False,
                        },
                        "title": {
                            "display": True,
                            "text": "€/l"
                        }
                    },
                },
            }
        )
    }

    data["stats"] = fillups.aggregate(
        Avg("consumption"), Sum("total_price"), Sum("distance_delta")
    )
    return data
