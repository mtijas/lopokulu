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
        sh 'docker exec lopokulu_app_1 python3 src/manage.py wait_for_database'
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
        publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('NEVER_STORE')
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

    stage('Publish') {
      parallel {
        stage('Publish development') {
          when { branch 'development' }
          steps {
            sh 'docker tag lopokulu mtijas/lopokulu:development'
            withCredentials([usernamePassword(credentialsId: 'lopokuluDockerHub', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              sh 'echo ${PASSWORD} | docker login -u $USERNAME --password-stdin'
              sh 'docker push --all-tags mtijas/lopokulu'
              sh 'docker logout'
            }
          }
        }

        stage('Publish production') {
          when {
            branch 'main'
            buildingTag()
          }
          steps {
            sh 'docker tag lopokulu mtijas/lopokulu:latest'
            sh 'docker tag lopokulu mtijas/lopokulu:$TAG_NAME'
            withCredentials([usernamePassword(credentialsId: 'lopokuluDockerHub', passwordVariable: 'PASSWORD', usernameVariable: 'USERNAME')]) {
              sh 'echo ${PASSWORD} | docker login -u $USERNAME --password-stdin'
              sh 'docker push --all-tags mtijas/lopokulu'
              sh 'docker logout'
            }
          }
        }
      }
    }

    stage('Deploy') {
      parallel {
        stage('Deploy development') {
          when { branch 'development' }
          steps {
            script {
              def remote = [:]
              remote.name = 'Löpökulu target'
              remote.host = DEPLOY_TARGET
              withCredentials([sshUserPrivateKey(credentialsId: 'ansible-jenkins', keyFileVariable: 'identity', passphraseVariable: 'passphrase', usernameVariable: 'userName')]) {
                remote.user = userName
                remote.identityFile = identity
                remote.passphrase = passphrase
                remote.allowAnyHosts = true
                sshCommand remote: remote, command: 'kubectl rollout restart -n lopokulu-dev deployment/app-depl'
              }
            }
          }
        }

        stage('Deploy production') {
          when {
            branch 'main'
            buildingTag()
          }
          steps {
            script {
              def remote = [:]
              remote.name = 'Löpökulu target'
              remote.host = DEPLOY_TARGET
              withCredentials([sshUserPrivateKey(credentialsId: 'ansible-jenkins', keyFileVariable: 'identity', passphraseVariable: 'passphrase', usernameVariable: 'userName')]) {
                remote.user = userName
                remote.identityFile = identity
                remote.passphrase = passphrase
                remote.allowAnyHosts = true
                sshCommand remote: remote, command: 'kubectl rollout restart -n lopokulu deployment/app-depl'
              }
            }
          }
        }
      }
    }

    stage('Cleanup') {
      steps {
        sh 'docker-compose -f docker-compose-testing.yaml down'
        sh 'docker system prune -a -f --volumes'
      }
    }
  }

  post {
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
    DEPLOY_TARGET = credentials('lopokulu-target-host')
    AXES_ENABLED = 'False'
  }
}
