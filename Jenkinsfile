pipeline {
  agent any
  environment { IMAGE = "secscan:${env.BUILD_NUMBER}" }
  stages {
    stage('Build image') {
      steps { sh 'podman build -t $IMAGE .' }
    }
    stage('Test') {
      steps { sh 'podman run --rm $IMAGE pytest -q' }
    }
  }
}
