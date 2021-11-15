FROM python:3.10-slim AS prebuild

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
