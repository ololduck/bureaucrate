pipeline {
  agent any
  stages {
    stage('test') {
      steps {
        isUnix()
        sh '''virtualenv --python=python3 .venv;
source .venv/bin/activate; pip install -r requirements_dev.txt; nosetest --with-doctests bureaucrate'''
      }
    }
  }
}