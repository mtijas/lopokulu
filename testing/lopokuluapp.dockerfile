FROM python:3.10-slim

    WORKDIR /lopokulu

    COPY requirements.txt .
    COPY .coveragerc .
    COPY testing/entrypoint.sh .

    RUN useradd -m jenkins
    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt
    RUN chmod +x ./entrypoint.sh
    RUN chown jenkins:jenkins /lopokulu

    USER jenkins

    ENTRYPOINT ["/lopokulu/entrypoint.sh"]
