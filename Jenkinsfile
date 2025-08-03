pipeline {
  agent any

  environment {
    OPENAI_API_KEY = credentials('OPENAI_API_KEY')
    IMAGE_NAME = "local-app"
    REPORT_JSON = "scan_output/trivy_report.json"    // Corrected path
    REPORT_MD = "reports/trivy_report.md"
    REPORT_HTML = "reports/trivy_report.html"
    PATH = "/usr/local/bin:${env.PATH}"
  }

  stages {

    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Inder1199/jenkins-agentic-ai-mvp-devsecops.git'
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

            docker build -t ${IMAGE_NAME} .
          '''
        }
      }
    }

    stage('Run Trivy Scan') {
      steps {
        sh '''
          mkdir -p scan_output
          trivy image --format json -o ${REPORT_JSON} ${IMAGE_NAME}
        '''
      }
    }

    stage('Generate Reports') {
      steps {
        sh '''
          mkdir -p reports
          python3 trivy_to_md.py ${REPORT_JSON} > ${REPORT_MD}
          python3 trivy_to_html.py ${REPORT_JSON} > ${REPORT_HTML}
        '''
      }
    }

    // stage('Patch Vulnerabilities (GPT Agent)') {
    //   steps {
    //     withEnv(['OPENAI_API_KEY=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']) {
    //       sh 'python3 patch_agent.py'
    //     }
    //   }
    // }

    stage('Patch Vulnerabilities (Ollama Agent)') {
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

  post {
    always {
      archiveArtifacts artifacts: 'scan_output/*.md', fingerprint: true
    }
  }
}
