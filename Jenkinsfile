pipeline {
  agent any

  triggers { githubPush() }

  environment {
    DH_IMAGE  = 'emanmansoor/midterm-fa23-bds-008'
    CONTAINER = 'midterm-app'
    STUDENT   = 'FA23-BDS-008'
    HOST      = '15.206.40.196'
  }

  stages {
    stage('Fetch latest data') {
      steps {
        checkout scm
        script {
          env.GIT_SHA = sh(script: 'git rev-parse HEAD', returnStdout: true).trim()
          env.AUTHOR_EMAIL = sh(script: 'git log -1 --pretty=format:%ae', returnStdout: true).trim()
          env.COMMITTER_EMAIL = sh(script: 'git log -1 --pretty=format:%ce', returnStdout: true).trim()
        }
        sh 'git log -1 --oneline'
        sh 'wc -l dataset/train.csv'
      }
    }

    stage('Train and build image') {
      steps {
        sh 'docker build --build-arg GIT_SHA=$GIT_SHA -t $DH_IMAGE:latest .'
      }
    }

    stage('Test') {
      steps {
        sh 'docker run --rm $DH_IMAGE:latest python test_pipeline.py'
      }
    }

    stage('Push to Docker Hub') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
          sh 'docker push $DH_IMAGE:latest'
          sh 'docker logout'
        }
      }
    }

    stage('Deploy') {
      steps {
        sh '''
          docker pull $DH_IMAGE:latest
          docker rm -f $CONTAINER || true
          docker run -d --name $CONTAINER --restart unless-stopped -p 8000:8000 $DH_IMAGE:latest
          for i in $(seq 1 20); do
            if curl -sf http://localhost:8000/metrics > /dev/null; then echo "App is up"; exit 0; fi
            sleep 3
          done
          echo "App did not start"
          docker logs $CONTAINER
          exit 1
        '''
        sh 'docker image prune -f'
      }
    }
  }

  post {
    always {
      script {
        def metrics = sh(script: 'curl -s http://localhost:8000/metrics || echo "not available"', returnStdout: true).trim()

        def recipient = env.AUTHOR_EMAIL ?: ''
        if (recipient.toLowerCase().contains('noreply')) { recipient = env.COMMITTER_EMAIL ?: '' }
        if (recipient.toLowerCase().contains('noreply')) { recipient = '' }

        if (recipient) {
          emailext(
            to: recipient,
            subject: "[${env.STUDENT}] MIDTERM build #${env.BUILD_NUMBER} - ${currentBuild.currentResult}",
            body: """Student Reg No: ${env.STUDENT}
Build: #${env.BUILD_NUMBER}
Result: ${currentBuild.currentResult}
Commit: ${env.GIT_SHA}
Pushed by: ${recipient}
Docker Hub image: ${env.DH_IMAGE}:latest
Metrics URL: http://${env.HOST}:8000/metrics
Metrics: ${metrics}
Build log: ${env.BUILD_URL}"""
          )
        } else {
          echo 'No usable committer email found, mail not sent'
        }
      }
    }
  }
}