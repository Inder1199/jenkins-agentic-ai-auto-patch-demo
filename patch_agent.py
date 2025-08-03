import os
import json
import sys
import time
import re
import openai
from openai.types.chat import ChatCompletion

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY not set.")
    sys.exit(1)

openai.api_key = api_key

# Validate Trivy scan report
trivy_report_path = "scan_output/trivy_report.json"
if not os.path.exists(trivy_report_path):
    print(f"❌ Missing Trivy report at {trivy_report_path}")
    sys.exit(1)

with open(trivy_report_path, "r") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Invalid JSON in Trivy report.")
        sys.exit(1)

results = data.get("Results", [])
if not results:
    print("✅ No results found in Trivy report.")
    sys.exit(0)

# Output file
output_path = "scan_output/gpt_patch_suggestions.md"
os.makedirs("scan_output", exist_ok=True)

with open(output_path, "w") as out:
    out.write("# 🛠️ GPT-Based Vulnerability Patch Suggestions\n\n")
    count = 0

    for target in results:
        for finding in target.get("Vulnerabilities", []):
            vuln_id = finding.get("VulnerabilityID")
            pkg_name = finding.get("PkgName")
            installed_version = finding.get("InstalledVersion")
            severity = finding.get("Severity")
            description = finding.get("Description", "")[:300]
            fixed_version = finding.get("FixedVersion", "")

            if not vuln_id or not pkg_name or not installed_version:
                continue  # Incomplete data

            # Optional: skip if no fixed version (you can remove this block if you want to keep all)
            if not fixed_version:
                continue

            prompt = (
                f"You are a DevSecOps engineer. Suggest a fix, patch, or mitigation for the following:\n"
                f"- CVE: {vuln_id}\n- Package: {pkg_name}\n- Version: {installed_version}\n"
                f"- Severity: {severity}\n- Description: {description}"
            )

            try:
                response: ChatCompletion = openai.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a DevSecOps assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    timeout=30
                )

                suggestion = response.choices[0].message.content.strip()

                # Escape Markdown characters
                suggestion = re.sub(r'([*_`])', r'\\\1', suggestion)

                out.write(f"## {vuln_id} ({pkg_name}@{installed_version})\n")
                out.write(f"**Severity**: {severity}  \n")
                out.write(f"**Fixed Version**: {fixed_version}\n\n")
                out.write(f"{suggestion}\n\n")
                count += 1

                time.sleep(1.5)

            except openai.RateLimitError:
                out.write(f"⚠️ Skipped {vuln_id}: Rate limit exceeded. Try again later.\n\n")
            except openai.APIError as e:
                out.write(f"⚠️ Skipped {vuln_id}: OpenAI API error - {e}\n\n")
            except Exception as e:
                out.write(f"⚠️ Skipped {vuln_id}: Unexpected error - {e}\n\n")

    print(f"✅ Patch suggestions written to {output_path} for {count} vulnerabilities.")
