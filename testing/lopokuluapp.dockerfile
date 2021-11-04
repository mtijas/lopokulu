FROM python:latest
  RUN useradd -d /home/jenkins -ms /bin/bash -g root -G sudo jenkins
  RUN pip install --upgrade pip
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY ./testing/entrypoint.sh /entrypoint.sh
  RUN chmod +x /entrypoint.sh
  USER jenkins
