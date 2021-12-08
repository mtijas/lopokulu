<!--
SPDX-FileCopyrightText: 2021 Jani Lehtinen
SPDX-FileCopyrightText: 2021 Markus Ijäs
SPDX-FileCopyrightText: 2021 Markus Murto

SPDX-License-Identifier: CC0-1.0
-->

# lopokulu

[![REUSE status](https://api.reuse.software/badge/github.com/mtijas/lopokulu)](https://api.reuse.software/info/github.com/mtijas/lopokulu)
![MAIN branch status](https://jenkins.tiko2020.trade/job/lopokulu/job/main/badge/icon?subject=Main)
![DEVELOPMENT branch status](https://jenkins.tiko2020.trade/job/lopokulu/job/development/badge/icon?subject=Development)

This is a work-in-progress project to create a Django web application for
vehicle fuel usage monitoring.

## Table of contents

* [Installation (for development)](#installation-for-development)
    * [Creating the necessary files](#creating-the-necessary-files)
        * [Docker Compose file](#docker-compose-file)
        * [.env file](#env-file)
        * [Nginx template](#nginx-template)
    * [Running](#running)
    * [Creating the superuser](#creating-the-superuser)
* [License](#license)

## Installation (for development)

The app is distributed as
[a Docker container](https://hub.docker.com/r/mtijas/lopokulu), but requires a
database server and a webserver.

### Creating the necessary files

Everything can be deployed with the following file and directory structure in
your working directory (whereever its convenient or appropriate for you, for
example a subdirectory in your home directory):

```
.
├── .env
├── docker-compose.yml
└── nginx-templates
   └── default.conf.template
```

#### Docker Compose file

The `docker-compose.yml` could look like this:
```
version: "3"

services:
  lopokuluapp:
    image: mtijas/lopokulu:development
    env_file:
      - .env
    depends_on:
      - postgres
    volumes:
      - staticfiles:/lopokulu/static/

  postgres:
    image: postgres:latest
    volumes:
      - psql-data:/var/lib/postgresql/data
    env_file:
      - .env

  web:
    image: nginx:latest
    volumes:
      - ./nginx-templates:/etc/nginx/templates
      - staticfiles:/srv/www/assets
    ports:
      - 8080:80
    depends_on:
      - lopokuluapp
    env_file:
      - .env

volumes:
  psql-data:
  staticfiles:
```

#### .env file

You can see from the Docker Compose file that we need to create two additional
files. `.env` is used to declare the needed environment variables, for example
with the following content:

```
DEBUG=True
ADMINER_DEFAULT_SERVER=postgres
POSTGRES_USER=lopokulu
POSTGRES_DB=lopokulu
POSTGRES_PASSWORD=lopokulu
POSTGRES_PORT=5432
POSTGRES_HOST=postgres
PGDATA=/var/lib/postgresql/data/pgdata
SECRET_KEY='django-insecure-!0#jh@%9*oz=b1^&!3khm6-5g)x2o2g89xr#i5-f0!jns&xbma'
NGINX_HOST=localhost
NGINX_PORT=80
```

You should at least change the `SECRET_KEY`.

#### Nginx template

Nginx also can be configured by writing a similar Nginx template in
`./nginx-templates/default.conf.template` (make sure this is the directory name
you configured in the Docker Compose file):

```
upstream lopokulu_upstream_wsgi {
    server lopokuluapp:8000 fail_timeout=0;
}

server {
  listen ${NGINX_PORT};

  location /static {
    autoindex on;
    alias /srv/www/assets/;
  }

  location / {
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    proxy_redirect off;

    if (!-f $request_filename) {
      proxy_pass http://lopokulu_upstream_wsgi;
    }
  }
}
```

### Running

Run these commands in the same directory where the Compose file is.

Launch the containers declared in the Compose file:
```
$ docker-compose up -d
```

Run the Django migrations:
```
$ docker exec -it $(basename $PWD)_lopokuluapp_1 python3 src/manage.py migrate
```

To replace `$(basename $PWD)_lopokuluapp_1`, you can find the literal container
name with:
```
$ docker ps | grep 'mtijas/lopokulu' | awk '{print $13}'
```

Then you can access the app in browser `http://localhost:8080/`.

The app can be stopped with:
```
$ docker-compose down
```

### Creating the superuser

The superuser can be created interactively with:
```
$ docker exec -it $(basename $PWD)_lopokuluapp_1 python3 src/manage.py createsuperuser
```

You might want to use the literal container name here again.

<!-- TODO(murtoM): add sections for app upgrading and usage -->

## License

The programming code is licensed under the MIT license. The up-to-date licensing and copyright information can be found on each file's header or in a separate `.license` file. Few files' copyright information (or the lack of copyright claim) is declared in `.reuse/dep5`, for example Django model migration files.
