pipeline {
  agent any

  environment {
    OPENAI_API_KEY = credentials('OPENAI_API_KEY')
    IMAGE_NAME = "local-app"
    REPORT_JSON = "trivy_report.json"
    REPORT_MD = "reports/trivy_report.md"
    REPORT_HTML = "reports/trivy_report.html"
    PATH = "/opt/homebrew/bin:$PATH"
  }

  stages {

    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Inder1199/jenkins-agentic-ai-mvp-devsecops.git'
      }
    }

    stage('Build Docker Image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME} .'
      }
    }

    stage('Run Trivy Scan') {
      steps {
        sh 'mkdir -p reports'
        sh 'trivy image --format json -o ${REPORT_JSON} ${IMAGE_NAME}'
      }
    }

    stage('Generate Reports') {
      steps {
        sh '''
          python3 trivy_to_md.py ${REPORT_JSON} > ${REPORT_MD}
          python3 trivy_to_html.py ${REPORT_JSON} > ${REPORT_HTML}
        '''
      }
    }

    stage('Patch Vulnerabilities (GPT Agent)') {
      steps {
        sh 'python3 patch_agent.py'
      }
    }

    stage('Archive Reports') {
      steps {
        archiveArtifacts artifacts: 'reports/*', fingerprint: true
      }
    }

    stage('Auto Commit & PR (Optional)') {
      when {
        expression { return env.GH_TOKEN != null }
      }
      steps {
        withCredentials([string(credentialsId: 'GH_TOKEN', variable: 'GH_TOKEN')]) {
          sh '''
            git config --global user.name "agentic-bot"
            git config --global user.email "agentic@example.com"

            git checkout -b patch/gpt-fixes || git checkout patch/gpt-fixes
            git add sample_app/vulnerable.py
            git commit -m "Agentic AI Patch: auto fix vulnerabilities"
            git push -u origin patch/gpt-fixes

            echo "${GH_TOKEN}" | gh auth login --with-token
            gh pr create --title "Auto patch via GPT Agent" --body "Patched critical vulnerabilities via Agentic AI." --base main
          '''
        }
      }
    }

  }

  post {
    always {
      echo 'Pipeline completed. Reports archived.'
    }
  }
}
