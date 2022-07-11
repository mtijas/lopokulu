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


FROM prebuild AS development

    COPY .coveragerc .

    COPY ./entrypoint-dev.sh ./entrypoint.sh
    RUN chmod +x ./entrypoint.sh

    COPY requirements.development.txt .
    RUN pip install -r requirements.development.txt

    COPY ./src ./src

    RUN chown -R lopokulu:lopokulu /lopokulu

    USER lopokulu

    CMD ["/lopokulu/entrypoint.sh"]


FROM prebuild AS production

    COPY ./entrypoint-production.sh ./entrypoint.sh
    RUN chmod +x ./entrypoint.sh

    COPY ./static ./static
    COPY ./src ./src

    RUN chown -R lopokulu:lopokulu /lopokulu

    USER lopokulu

    CMD ["/lopokulu/entrypoint.sh"]
