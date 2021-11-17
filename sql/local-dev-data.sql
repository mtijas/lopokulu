-- SPDX-FileCopyrightText: 2021 Jani Lehtinen
-- SPDX-FileCopyrightText: 2021 Markus Ijäs
-- SPDX-FileCopyrightText: 2021 Markus Murto
--
-- SPDX-License-Identifier: CC0-1.0

INSERT INTO "manager_person" ("id", "password", "last_login", "is_superuser", "email", "is_active", "is_admin", "is_staff") VALUES
(1,	'pbkdf2_sha256$260000$HvWDennzaccvs6vV7sPhxc$7h4QgeoLRpHKgbCmpF0w9NWyNMtKkv5Yd3FhYvjIyRg=',	'2021-10-14 08:12:58.382745+00',	'1',	'lopokulu@foo.bar',	'1',	'1',	'1');

INSERT INTO "manager_vehicle" ("id", "register_number", "name") VALUES
(1,	'CBA-321',	'Ensimmäinen auto'),
(2,	'ABC-123',	'Toinen auto');

INSERT INTO "manager_vehicleuser" ("id", "role", "person_id", "vehicle_id") VALUES
(1,	'RO',	1,	1),
(2,	'DR',	1,	2);
