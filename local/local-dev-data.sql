-- SPDX-FileCopyrightText: 2021 Jani Lehtinen
-- SPDX-FileCopyrightText: 2021 Markus Ijäs
-- SPDX-FileCopyrightText: 2021 Markus Murto
--
-- SPDX-License-Identifier: CC0-1.0

INSERT INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined") VALUES
(1,	'pbkdf2_sha256$260000$7WXt5WC97Qqd6yCfQYka9M$s3m2DwMrNylYVpQ7LYOgTewtLVTnKfZS/1L1e/Kqn6w=',	'2021-10-07 08:19:20+00',	'1',	'admin',	'',	'',	'',	'1',	'1',	'2021-09-23 13:14:55+00');

INSERT INTO "fillup_fillup" ("id", "price", "amount", "distance", "vehicle_id") VALUES
(1,	1.507,	48.7,	215485,	1);

NSERT INTO "fillup_person" ("id", "user_id") VALUES
(1,	1);

INSERT INTO "fillup_vehicle" ("id", "register_number", "name") VALUES
(1,	'ABC-123',	'Hieno punainen Golf');

INSERT INTO "fillup_vehicleuser" ("id", "role", "person_id", "vehicle_id") VALUES
(1,	'RO',	1,	1);

