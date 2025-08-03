import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("scan_output/trivy_report.json", "r") as f:
    data = json.load(f)

for vuln in data.get("Results", []):
    for finding in vuln.get("Vulnerabilities", []):
        prompt = f"Suggest a patch or mitigation for CVE: {finding['VulnerabilityID']}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a DevSecOps assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        suggestion = response.choices[0].message.content
        print(f"Fix suggestion for {finding['VulnerabilityID']}:\n{suggestion}\n")
