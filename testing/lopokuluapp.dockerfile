FROM python:latest
  RUN mkdir /app
  WORKDIR /app
  RUN pip install --upgrade pip
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY ./app /app
  COPY ./testing/testing-entrypoint.sh /testing-entrypoint.sh
  RUN chmod +x /testing-entrypoint.sh
