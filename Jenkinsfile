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
        dir('agentic-mvp') {
          sh 'docker context use $DOCKER_CONTEXT'
          sh 'docker version'
          sh 'cat Dockerfile' 
          sh 'pwd'
          sh 'ls -la'
          sh 'sh "docker build -t local-app -f /Users/user/.jenkins/workspace/agentic-ai-mvp/Dockerfile /Users/user/.jenkins/workspace/agentic-ai-mvp"'
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

