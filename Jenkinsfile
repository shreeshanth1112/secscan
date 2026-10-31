pipeline {
  agent any
  environment {
    DH_USER  = "shreeshanth1112"
    IMAGE    = "docker.io/${DH_USER}/secscan"
    TAG      = "${env.BUILD_NUMBER}"
    DH_CREDS = credentials('dockerhub')
  }
  stages {
    stage('Build image') {
      steps { sh 'podman build -t $IMAGE:$TAG .' }
    }
    stage('Test') {
      steps { sh 'podman run --rm $IMAGE:$TAG pytest -q' }
    }
    stage('Push to Docker Hub') {
      steps {
        sh '''
          echo "$DH_CREDS_PSW" | podman login docker.io -u "$DH_CREDS_USR" --password-stdin
          podman tag $IMAGE:$TAG $IMAGE:latest
          podman push $IMAGE:$TAG
          podman push $IMAGE:latest
        '''
      }
    }
  }
}
