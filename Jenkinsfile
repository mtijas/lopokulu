pipeline {
  agent any
  stages {
    stage('Pull development') {
      steps {
        git(url: 'https://github.com/mtijas/lopokulu', branch: 'development', poll: true)
      }
    }

    stage('Run docker-compose') {
      steps {
        sh '''cd lopokulu
docker-compose -d -f docker-compose-testing.yaml up --build'''
      }
    }

    stage('Run tests') {
      steps {
        sh '''sudo docker exec -it lopokulu_lopokuluapp_1 sh
cd src
python3 manage.py unittest'''
      }
    }

  }
}