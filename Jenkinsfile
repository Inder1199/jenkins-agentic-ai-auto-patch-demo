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
          echo "PWD: $(pwd)"
          echo "Listing:"
          ls -la
        '''
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          docker build -t local-app .
        '''
      }
    }

    stage('Install Trivy') {
      steps {
        sh '''
          if ! command -v trivy >/dev/null 2>&1; then
            echo "Installing Trivy..."
            wget -q https://github.com/aquasecurity/trivy/releases/download/v${TRIVY_VERSION}/trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            tar zxvf trivy_${TRIVY_VERSION}_Linux-64bit.tar.gz
            sudo mv trivy /usr/local/bin/
          else
            echo "Trivy is already installed."
          fi
        '''
      }
    }

    stage('Trivy Scan') {
      steps {
        sh '''
          mkdir -p reports
          trivy fs --format json --output reports/trivy_report.json sample_app/
          ls -lh reports/trivy_report.json
        '''
      }
    }

    stage('Patch Agent') {
      when {
        expression { fileExists('patch_agent.py') }
      }
      steps {
        sh '''
          echo "Running patch agent"
          python3 patch_agent.py
        '''
      }
    }

    stage('Generate Markdown Report') {
      steps {
        sh '''
          python3 trivy_to_md.py reports/trivy_report.json > reports/trivy_report.md
        '''
      }
    }

    stage('Archive Reports') {
      steps {
        archiveArtifacts artifacts: 'reports/**', fingerprint: true
      }
    }
  }
}
