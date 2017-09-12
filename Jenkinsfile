pipeline {
  agent any
  stages {
    stage('test') {
      steps {
        parallel(
          "test": {
            isUnix()
            sh '''virtualenv --python=python3 .venv;
source .venv/bin/activate;
'''
            
          },
          "build": {
            sh 'python setup.py build'
            
          }
        )
      }
    }
  }
}