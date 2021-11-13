FROM python:3.10-slim

    WORKDIR /lopokulu

    COPY requirements.txt .
    COPY .coveragerc .

    RUN useradd -ms /bin/bash lopokulu
    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt
    RUN chown lopokulu:lopokulu /lopokulu

    USER lopokulu

    CMD ["gunicorn", "--chdir", "/lopokulu/src", "lopokulu.wsgi:application", "--bind", "0.0.0.0:8000"]
