pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'docker-compose -f docker-compose-testing.yaml up -d --build'
      }
    }

    stage('Test') {
      steps {
        sh 'docker exec lpkulu_lopokuluapp_1 bash -c "python3 /src/manage.py test /src/"'
      }
    }

  }
  environment {
    DEBUG = 'True'
    POSTGRES_DB = 'lopokulu'
    POSTGRES_PORT = '5432'
    POSTGRES_HOST = 'postgres'
    PGDATA = '/var/lib/postgresql/data/pgdata'
    NGINX_HOST = 'localhost'
    NGINX_PORT = '80'
    POSTGRES_USER = credentials('lopokulu-postgres-user')
    POSTGRES_PASSWORD = credentials('lopokulu-postgres-password')
    SECRET_KEY = credentials('lopokulu-django-secret-key')
  }
}