// SPDX-FileCopyrightText: 2021 Jani Lehtinen
// SPDX-FileCopyrightText: 2021 Markus Ijäs
// SPDX-FileCopyrightText: 2021 Markus Murto
//
// SPDX-License-Identifier: CC0-1.0

pipeline {
  agent any

  stages {
    stage('Prepare tests') {
      steps {
        sh 'docker-compose -f docker-compose-testing.yaml up -d --build'
      }
    }

    stage('Test') {
      steps {
        sh 'docker exec lopokulu_app_1 coverage run src/manage.py test src'
      }
    }

    stage('Generate coverage reports') {
      steps {
        sh 'docker exec lopokulu_app_1 coverage xml'
        sh 'docker cp lopokulu_app_1:/lopokulu/coverage.xml .'
      }
    }

    stage('Collect static') {
      steps {
        sh 'docker exec lopokulu_app_1 python3 src/manage.py collectstatic --no-input'
        sh 'docker cp lopokulu_app_1:/lopokulu/static ./static'
      }
    }

    stage('Build') {
      steps {
        sh 'docker build --target production -t lopokulu .'
      }
    }

    stage('Deliver Development') {
      when {
        branch 'development'
      }
      steps {
        sh 'docker tag lopokulu mtijas/lopokulu:development'

        withCredentials([usernamePassword(credentialsId: 'lopokuluDockerHub', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
          sh 'docker login -u $USERNAME -p $PASSWORD'
          sh 'docker push mtijas/lopokulu:development'
        }

        sh 'docker rmi mtijas/lopokulu:development'
      }
    }

    stage('Cleanup') {
      steps {
        sh 'docker-compose -f docker-compose-testing.yaml down'
        sh 'docker rmi lopokulu'
        sh 'docker rmi lopokulu:testing'
      }
    }
  }

  post {
    success {
      publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
    }

    always {
      cleanWs()
    }
  }

  environment {
    DEBUG = 'True'
    POSTGRES_DB = 'lopokulu'
    POSTGRES_PORT = '5432'
    POSTGRES_HOST = 'postgres'
    PGDATA = '/var/lib/postgresql/data/pgdata'
    POSTGRES_USER = credentials('lopokulu-postgres-user')
    POSTGRES_PASSWORD = credentials('lopokulu-postgres-password')
    SECRET_KEY = credentials('lopokulu-django-secret-key')
  }
}
