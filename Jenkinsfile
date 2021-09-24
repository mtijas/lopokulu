// SPDX-FileCopyrightText: 2021 Jani Lehtinen
// SPDX-FileCopyrightText: 2021 Markus Ijäs
// SPDX-FileCopyrightText: 2021 Markus Murto
//
// SPDX-License-Identifier: CC0-1.0

pipeline {
  agent any
  stages {
    stage('First step lol') {
      steps {
        git(url: 'https://github.com/mtijas/lopokulu', branch: 'development', poll: true)
      }
    }

  }
}