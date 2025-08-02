pipeline {
  agent any

  stages {
    stage('Clone') {
      steps {
        checkout scm
        sh 'pwd && ls -la'
      }
    }
    stage('Build Docker Image') {
      steps {
        dir('agentic-mvp') {
          sh 'docker build -t local-app .'
        }
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
