FROM python:3.10-slim

    WORKDIR /lopokulu

    COPY requirements.txt .
    COPY .coveragerc .
    COPY local/entrypoint.sh .

    RUN useradd -m lopokulu
    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt
    RUN chmod +x ./entrypoint.sh
    RUN chown lopokulu:lopokulu /lopokulu

    USER lopokulu

    ENTRYPOINT ["/lopokulu/entrypoint.sh"]
