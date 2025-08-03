import json
import os
import sys
from openai import OpenAI

# Initialize OpenAI client with the available model
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-3.5-turbo"  # Use the accessible model

# Load Trivy scan results
trivy_report = "scan_output/trivy_report.json"
if not os.path.exists(trivy_report):
    print("❌ Trivy report not found at scan_output/trivy_report.json")
    sys.exit(1)

with open(trivy_report, "r") as f:
    data = json.load(f)

results = data.get("Results", [])
if not results:
    print("✅ No scan results found in Trivy report.")
    sys.exit(0)

print(f"🔍 Found {len(results)} target(s) in Trivy scan report")

patch_suggestions = []
processed_count = 0
skipped_count = 0

for idx, target in enumerate(results):
    target_name = target.get("Target", "unknown")
    vulns = target.get("Vulnerabilities", [])

    if not vulns:
        print(f"⏭️ No vulnerabilities in: {target_name}")
        continue

    print(f"\n📦 Target {idx+1}: {target_name} — {len(vulns)} vulnerabilities")

    for vuln in vulns:
        vuln_id = vuln.get("VulnerabilityID")
        pkg = vuln.get("PkgName")
        installed = vuln.get("InstalledVersion")
        fixed = vuln.get("FixedVersion")
        severity = vuln.get("Severity")
        description = vuln.get("Description", "No description available.")

        if not vuln_id or not pkg:
            skipped_count += 1
            continue

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
            suggestion = response.choices[0].message.content.strip()
            patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
            processed_count += 1
        except Exception as e:
            print(f"⚠️ Failed to fetch suggestion for {vuln_id}: {e}")
            continue

# Write output
output_path = "scan_output/gpt_patch_suggestions.md"
if patch_suggestions:
    os.makedirs("scan_output", exist_ok=True)
    with open(output_path, "w") as f:
        f.write("# GPT-Generated Patch Suggestions\n\n")
        f.write("\n---\n\n".join(patch_suggestions))
    print(f"\n✅ Patch suggestions written to `{output_path}`")
else:
    print("\n⚠️ No patch suggestions generated. Please verify scan data and model access.")

print(f"\n📊 Summary:\n- Processed: {processed_count}\n- Skipped: {skipped_count}")
