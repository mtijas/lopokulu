# SPDX-FileCopyrightText: 2021 Jani Lehtinen
# SPDX-FileCopyrightText: 2021 Markus Ijäs
# SPDX-FileCopyrightText: 2021 Markus Murto
#
# SPDX-License-Identifier: CC0-1.0

FROM python:3.10-slim AS prebuild

    EXPOSE 8000

    WORKDIR /lopokulu

    RUN useradd -ms /bin/bash lopokulu
    RUN mkdir /lopokulu/static
    RUN pip install --upgrade pip

    COPY requirements.production.txt .
    RUN pip install -r requirements.production.txt

    COPY ./src ./src


FROM prebuild AS development

    COPY .coveragerc .

    COPY ./entrypoint.sh .
    RUN chmod +x ./entrypoint.sh

    RUN chown -R lopokulu:lopokulu /lopokulu

    COPY requirements.development.txt .
    RUN pip install -r requirements.development.txt

    USER lopokulu

    CMD ["/lopokulu/entrypoint.sh"]


FROM prebuild AS production

    COPY ./static ./static

    RUN chown -R lopokulu:lopokulu /lopokulu

    USER lopokulu

    CMD ["gunicorn", "--chdir", "/lopokulu/src", "lopokulu.wsgi:application", "--bind", "0.0.0.0:8000"]
