import json
import os
import sys
import time
from openai import OpenAI

# Environment variable check
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    print("❌ OPENAI_API_KEY is not set.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)
MODEL = "gpt-3.5-turbo"

# Load Trivy scan report
TRIVY_REPORT = "scan_output/trivy_report.json"
if not os.path.exists(TRIVY_REPORT):
    print("❌ Trivy report not found at scan_output/trivy_report.json")
    sys.exit(1)

with open(TRIVY_REPORT, "r") as f:
    data = json.load(f)

results = data.get("Results", [])
if not results:
    print("✅ No scan results found in Trivy report.")
    sys.exit(0)

print(f"🔍 Found {len(results)} target(s) in Trivy scan report")

# Collect only top 2 CRITICAL vulnerabilities
critical_vulns = []
for target in results:
    for vuln in target.get("Vulnerabilities", []):
        if vuln.get("Severity") == "CRITICAL":
            critical_vulns.append((target.get("Target", "unknown"), vuln))
        if len(critical_vulns) >= 2:
            break
    if len(critical_vulns) >= 2:
        break

if not critical_vulns:
    print("✅ No CRITICAL vulnerabilities found. Nothing to process.")
    sys.exit(0)

print(f"🚨 Selected {len(critical_vulns)} CRITICAL vulnerabilities for patch suggestion")

patch_suggestions = []

def get_patch_suggestion(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a security DevOps assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT request failed: {e}")
        return None

# Process each critical vulnerability
for target_name, vuln in critical_vulns:
    vuln_id = vuln.get("VulnerabilityID")
    pkg = vuln.get("PkgName")
    installed = vuln.get("InstalledVersion")
    fixed = vuln.get("FixedVersion")
    severity = vuln.get("Severity")
    description = vuln.get("Description", "No description available.")

    print(f"\n📦 Processing: {vuln_id} in {pkg} ({severity})")

    prompt = (
        f"Vulnerability ID: {vuln_id}\n"
        f"Package: {pkg}\n"
        f"Installed Version: {installed}\n"
        f"Fixed Version: {fixed}\n"
        f"Severity: {severity}\n"
        f"Description: {description}\n\n"
        "Suggest a patch or mitigation steps for this vulnerability in markdown format. "
        "Keep it concise and clear."
    )

    suggestion = get_patch_suggestion(prompt)
    if suggestion:
        patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
    else:
        print(f"⚠️ Skipped {vuln_id} due to GPT failure.")

# Write results
output_path = "scan_output/gpt_patch_suggestions.md"
if patch_suggestions:
    os.makedirs("scan_output", exist_ok=True)
    with open(output_path, "w") as f:
        f.write("# GPT-Generated Patch Suggestions (PoC)\n\n")
        f.write("\n---\n\n".join(patch_suggestions))
    print(f"\n✅ Patch suggestions written to `{output_path}`")
else:
    print("\n⚠️ No suggestions generated. Check GPT access and try again.")
