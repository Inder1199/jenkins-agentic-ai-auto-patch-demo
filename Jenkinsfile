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

        stage('Generate HTML Report') {
      steps {
        sh '''
          python3 trivy_to_html.py reports/trivy_report.json
        '''
      }
    }

    stage('Git Commit + Create Auto Patch MR') {
      when {
        expression { fileExists('patch_suggestion.txt') }
      }
      steps {
        sh '''
          git config --global user.name "agentic-ai-bot"
          git config --global user.email "bot@example.com"

          git checkout -b auto-patch-branch
          git add reports/*.md reports/*.html patch_suggestion.txt
          git commit -m "Agentic AI: Auto Patch Suggestions and Report"
          
          # Push branch and create MR using GitHub CLI
          git push origin auto-patch-branch

          if ! command -v gh >/dev/null 2>&1; then
            echo "Installing GitHub CLI..."
            type -p curl >/dev/null || (apt update && apt install curl -y)
            curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
            curl -fsSL https://cli.github.com/packages/githubcli.list | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
            sudo apt update && sudo apt install gh -y
          fi

          echo "Creating Pull Request using GitHub CLI..."
          gh auth login --with-token < ${HOME}/.gh_token  # ensure token is securely available
          gh pr create --title "Agentic AI Patch MR" --body "Auto-generated MR with patches and vulnerability report" --base main
        '''
      }
    }

  }
}
