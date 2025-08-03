import os
import openai
import json

# Set API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("trivy_report.json", "r") as f:
    data = json.load(f)

# Example GPT call (simplified)
for vuln in data.get("Results", []):
    for finding in vuln.get("Vulnerabilities", []):
        prompt = f"Suggest a patch or mitigation for CVE: {finding['VulnerabilityID']}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a DevSecOps assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        suggestion = response.choices[0].message.content
        print(f"Fix suggestion for {finding['VulnerabilityID']}:\n{suggestion}\n")
