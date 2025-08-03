import json
import os
import sys
from openai import OpenAI

# Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load Trivy JSON report
report_path = "scan_output/trivy_report.json"
output_path = "scan_output/gpt_patch_suggestions.md"

if not os.path.exists(report_path):
    print("❌ Trivy report not found at:", report_path)
    sys.exit(1)

with open(report_path, "r") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError as e:
        print("❌ Failed to parse JSON report:", e)
        sys.exit(1)

results = data.get("Results", [])
if not results:
    print("✅ No results in Trivy report.")
    sys.exit(0)

patch_suggestions = []
processed_count = 0
skipped_count = 0

print(f"🔍 Found {len(results)} scanned targets\n")

for idx, target in enumerate(results):
    target_name = target.get("Target", "unknown")
    vulns = target.get("Vulnerabilities", [])

    if not vulns:
        print(f"⏭️ No vulnerabilities in {target_name}")
        continue

    print(f"\n📦 [{idx+1}] {target_name} — {len(vulns)} vulnerability(ies)")

    for vuln in vulns:
        vuln_id = vuln.get("VulnerabilityID")
        pkg = vuln.get("PkgName")
        installed = vuln.get("InstalledVersion")
        fixed = vuln.get("FixedVersion", "N/A")
        severity = vuln.get("Severity", "Unknown")
        description = vuln.get("Description", "No description.")

        if not vuln_id or not pkg:
            skipped_count += 1
            continue

        prompt = (
            f"You're a security DevOps assistant.\n"
            f"Here is a vulnerability found in a scan:\n\n"
            f"Vulnerability ID: {vuln_id}\n"
            f"Package: {pkg}\n"
            f"Installed Version: {installed}\n"
            f"Fixed Version: {fixed}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n\n"
            f"Suggest a patch or mitigation steps for this CVE in markdown format. "
            f"Keep it short, clear, and actionable."
        )

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=400,
            )
            suggestion = response.choices[0].message.content.strip()
            patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
            processed_count += 1

        except Exception as e:
            print(f"⚠️ Error fetching suggestion for {vuln_id}: {e}")
            continue

# Write suggestions to markdown file
if patch_suggestions:
    os.makedirs("scan_output", exist_ok=True)
    with open(output_path, "w") as f:
        f.write("# 🔧 GPT-Generated Patch Suggestions\n\n")
        f.write("\n---\n\n".join(patch_suggestions))
    print(f"\n✅ Patch suggestions saved to: {output_path}")
else:
    print("\n⚠️ No suggestions generated.")

print(f"\n📊 Summary:\n- Processed: {processed_count}\n- Skipped: {skipped_count}")
