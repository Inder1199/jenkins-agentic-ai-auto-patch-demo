pipeline {
  agent any
  environment {
    TRIVY_VERSION = "0.51.1"
    PATH = "/usr/local/bin:${env.PATH}"
    DOCKER_CONTEXT = "desktop-linux"
  }

  stages {
    stage('Check Working Dir') {
      steps {
        sh '''
          echo "Present Working Directory:"
          pwd
          echo "Contents:"
          ls -la
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        dir("${env.WORKSPACE}") {
          sh '''
            echo "Present Working Directory:"
            pwd
            echo "Contents:"
            ls -la
    
            docker build -t local-app .
          '''
        }
  }
    }

    stage('Install Trivy (if missing)') {
      steps {
        sh '''
          if ! command -v trivy >/dev/null 2>&1; then
            echo "Installing Trivy..."
            wget https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            tar zxvf trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            sudo mv trivy /usr/local/bin/
          else
            echo "Trivy already installed"
          fi
        '''
      }
    }

    stage('Trivy Scan') {
      steps {
        dir("${env.WORKSPACE}") {
          sh '''
            trivy fs --format json --output trivy_report.json sample_app/
            ls -lh trivy_report.json
          '''
        }
      }
    }

    stage('Run Patch Agent') {
      steps {
        dir("${env.WORKSPACE}") {
          sh '''
            echo "Running patch agent from:"
            pwd
            ls -la
            python3 patch_agent.py
          '''
        }
      }
    }

    stage('Archive Trivy Report') {
      steps {
        dir("${env.WORKSPACE}") {
          archiveArtifacts artifacts: 'trivy_report.json', fingerprint: true
        }
      }
}
  }
}

