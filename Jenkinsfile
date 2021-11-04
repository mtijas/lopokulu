pipeline {
  agent any
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
  stages {
    stage('First step lol') {
      steps {
        git(url: 'https://github.com/mtijas/lopokulu', branch: 'development', poll: true)
      }
    }

  }
}
