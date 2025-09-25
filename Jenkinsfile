pipeline {
  agent any

  environment {
    OPENAI_API_KEY = credentials('OPENAI_API_KEY')
    IMAGE_NAME = "local-app"
    REPORT_JSON = "scan_output/trivy_report.json"
    REPORT_MD = "reports/trivy_report.md"
    REPORT_HTML = "reports/trivy_report.html"
    PATCH_HTML = "scan_output/gpt_patch_suggestions.html"
    PATH = "/usr/local/bin:${env.PATH}"
  }

  stages {

    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Inder1199/jenkins-agentic-ai-auto-patch-demo.git'
      }
    }

    stage('Build Docker Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-hub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            echo "🔑 Logging in to Docker Hub..."
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
    
            docker build -t ${IMAGE_NAME} .
            docker logout
          '''
        }
      }
    }


    stage('Start Ollama') {
      steps {
        sh '''
          if ! pgrep -x "ollama" > /dev/null; then
            echo "🚀 Starting Ollama server..."
            nohup ollama serve > ollama.log 2>&1 &
            sleep 10
          else
            echo "✅ Ollama already running."
          fi

          echo "📥 Pulling llama3 model..."
          ollama pull llama3 || true
        '''
      }
    }

    stage('Run Trivy Scan') {
      steps {
        sh '''
          mkdir -p scan_output
          echo "📥 Updating Trivy DB..."
          trivy image --download-db-only
          echo "🔍 Running Trivy scan..."
          trivy image --severity CRITICAL --format json -o ${REPORT_JSON} ${IMAGE_NAME}
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

    stage('Patch Vulnerabilities (Ollama Agent)') {
      steps {
        sh 'python3 patch_agent.py'
      }
    }

    stage('Convert GPT Patch Suggestions to HTML') {
      steps {
        sh '''
          mkdir -p scan_output
          echo "📂 Contents of scan_output before conversion:"
          ls -la scan_output || true

          if [ -f scan_output/gpt_patch_suggestions.md ]; then
            echo "✅ Found gpt_patch_suggestions.md, converting to HTML..."
            python3 -c "import markdown, pathlib; pathlib.Path('scan_output/gpt_patch_suggestions.html').write_text(markdown.markdown(pathlib.Path('scan_output/gpt_patch_suggestions.md').read_text()))"
          else
            echo "⚠️ No gpt_patch_suggestions.md found, skipping HTML conversion."
          fi
        '''
      }
    }

    stage('Auto Commit & PR (Mandatory)') {
      steps {
        withCredentials([string(credentialsId: 'GH_TOKEN', variable: 'GH_TOKEN')]) {
          sh '''
            git config --global user.name "Inder1199"
            git config --global user.email "inder1199@gmail.com"

            git clean -fd
            git checkout -b patch/gpt-fixes || git checkout patch/gpt-fixes

            git add sample_app/vulnerable.py || true
            git add scan_output/gpt_patch_suggestions.md || true
            git commit -m "Agentic AI Patch: auto fix vulnerabilities" || echo "No changes to commit"
            git push -u origin patch/gpt-fixes || echo "Push failed or already exists"

            curl -s -X POST -H "Authorization: token ${GH_TOKEN}" \
              -H "Accept: application/vnd.github+json" \
              https://api.github.com/repos/Inder1199/jenkins-agentic-ai-mvp-devsecops/pulls \
              -d '{
                "title": "Auto patch via GPT Agent",
                "body": "Patched critical vulnerabilities via Agentic AI.",
                "head": "patch/gpt-fixes",
                "base": "main"
              }' || echo "PR may already exist or failed"
          '''
        }
      }
    }

    stage('Archive Reports') {
      steps {
        script {
          if (fileExists('reports')) {
            archiveArtifacts artifacts: 'reports/*', fingerprint: true
          } else {
            echo "No report artifacts found in 'reports/'"
          }

          if (fileExists('scan_output/gpt_patch_suggestions.md')) {
            archiveArtifacts artifacts: 'scan_output/*.md', fingerprint: true
          } else {
            echo "No Markdown report found in 'scan_output/'"
          }

          def htmlFiles = sh(script: "find scan_output -name '*.html' | wc -l", returnStdout: true).trim()
          if (htmlFiles != "0") {
            archiveArtifacts artifacts: 'scan_output/*.html', fingerprint: true
          } else {
            echo "No HTML files found to archive in 'scan_output/'"
          }
        }
      }
    }

  }

  post {
    always {
      echo 'Pipeline completed. Reports and patch suggestions archived.'
    }
  }

}
