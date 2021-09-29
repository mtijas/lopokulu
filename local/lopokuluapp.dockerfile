FROM python:latest
  RUN pip install --upgrade pip
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY local/entrypoint.sh /entrypoint.sh
  RUN chmod +x /entrypoint.sh
