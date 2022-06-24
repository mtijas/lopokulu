# SPDX-FileCopyrightText: 2022 Markus Ijäs
#
# SPDX-License-Identifier: MIT

from equipment.models import Equipment


def user_has_role_for_equipment(
    user_id: int,
    measurement_type: str,
    equipment_id: int = None,
    allowed_roles: list[str] = ["USER", "ADMIN"],
):
    if equipment_id is None:
        return Equipment.objects.filter(
            allowed_measurements__contains=measurement_type,
            equipmentuser__user_id=user_id,
            equipmentuser__role__in=allowed_roles,
        ).exists()
    else:
        return Equipment.objects.filter(
            pk=equipment_id,
            allowed_measurements__contains=measurement_type,
            equipmentuser__user_id=user_id,
            equipmentuser__role__in=allowed_roles,
        ).exists()

def fetch_users_equipment(user):
    """Fetches equipment user has access to. Fetches all equipment for superusers"""
    # @TODO: Unit tests
    if user.is_superuser:
        return Equipment.objects.all()

    return Equipment.objects.filter(equipmentuser__user_id=user.id)
