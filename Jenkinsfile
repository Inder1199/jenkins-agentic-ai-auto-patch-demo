pipeline {
  agent {
    docker {
      image 'docker:24.0.5' // you can use any recent Docker image
      args '-v /var/run/docker.sock:/var/run/docker.sock' // enables Docker inside Jenkins agent
    }
  }

  environment {
    TRIVY_VERSION = "0.51.1"
  }

  stages {
    stage('Prepare') {
      steps {
        sh '''
          echo "Current directory:"
          pwd
          echo "Files:"
          ls -la
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        dir('agentic-mvp') {
          sh 'docker build -t local-app .'
        }
      }
    }

    stage('Install Trivy') {
      steps {
        sh '''
          if ! command -v trivy >/dev/null 2>&1; then
            echo "Installing Trivy..."
            wget https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            tar zxvf trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            mv trivy /usr/local/bin/
          else
            echo "Trivy is already installed"
          fi
        '''
      }
    }

    stage('Trivy Scan') {
      steps {
        dir('agentic-mvp') {
          sh 'trivy image --format json -o trivy_report.json local-app'
        }
      }
    }

    stage('Run Patch Agent') {
      steps {
        dir('agentic-mvp') {
          sh 'python3 patch_agent.py'
        }
      }
    }
  }
}

