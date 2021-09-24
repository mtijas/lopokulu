-- SPDX-FileCopyrightText: 2021 Jani Lehtinen
-- SPDX-FileCopyrightText: 2021 Markus Ijäs
-- SPDX-FileCopyrightText: 2021 Markus Murto
--
-- SPDX-License-Identifier: CC0-1.0

INSERT INTO "auth_user" ("id", "password", "last_login", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined") VALUES
(1,	'pbkdf2_sha256$260000$7WXt5WC97Qqd6yCfQYka9M$s3m2DwMrNylYVpQ7LYOgTewtLVTnKfZS/1L1e/Kqn6w=',	'2021-09-23 13:16:14.371703+00',	'1',	'admin',	'',	'',	'',	'1',	'1',	'2021-09-23 13:14:55.180726+00');
