# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from datetime import timedelta

from django import template
from django.db.models import Avg, Sum
from django.utils.timezone import now

from fillup.models import Fillup

register = template.Library()


@register.inclusion_tag("fillup/tags/equipment_stats.html")
def fillup_equipment_stats(equipment, start_dt=31, stop_dt=now(), mode: str = None):
    """Collects fillup stats for datetime range for specific equipment"""
    " TODO: Unit test mode"
    if mode == "current year":
        start_dt = now().replace(day=1, month=1)
    elif type(start_dt) is int:
        start_dt = now() - timedelta(days=start_dt)

    data = {
        "equipment": equipment,
        "start_dt": start_dt,
        "stop_dt": stop_dt,
        "mode": mode,
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
    )

    if not fillups:
        return data

    data["stats"] = fillups.aggregate(
        Avg("consumption"), Sum("total_price"), Sum("distance_delta")
    )
    return data
