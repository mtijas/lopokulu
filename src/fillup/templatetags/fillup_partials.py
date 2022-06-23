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
def equipment_fillup_stats(equipment, days: int = 31):
    """Collects fillup stats for n days before today for specific equipment"""
    data = {
        "equipment": equipment,
        "days": days,
        "stats": {
            "consumption__avg": 0,
            "total_price__sum": 0,
            "distance_delta__sum": 0,
        },
    }

    addition_date_limit = now() - timedelta(days=days)
    fillups = Fillup.objects.filter(
        addition_date__gte=addition_date_limit, equipment=equipment
    )

    if not fillups:
        return data

    data["stats"] = fillups.aggregate(
        Avg("consumption"), Sum("total_price"), Sum("distance_delta")
    )
    return data
