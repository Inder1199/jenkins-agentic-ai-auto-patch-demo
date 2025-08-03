import json
import openai
import os
import sys

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load Trivy scan results
try:
    with open("scan_output/trivy_report.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("❌ Trivy report not found at scan_output/trivy_report.json")
    sys.exit(1)

results = data.get("Results", [])
if not results:
    print("✅ No scan results found in Trivy report.")
    sys.exit(0)

print(f"🔍 Found {len(results)} result(s) in Trivy scan report\n")

patch_suggestions = []
processed_count = 0
skipped_count = 0

for idx, target in enumerate(results):
    target_name = target.get("Target", "unknown")
    vulns = target.get("Vulnerabilities", [])

    if not vulns:
        print(f"⏭️ No vulnerabilities in target: {target_name}")
        continue

    print(f"📦 Target {idx+1}: {target_name} — {len(vulns)} vulnerabilities")

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
            "Suggest a patch or mitigation steps for this vulnerability. "
            "Keep the explanation concise and use markdown format if relevant."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a security DevOps assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,
            )
            suggestion = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Failed to fetch suggestion for {vuln_id}: {e}")
            continue

        patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
        processed_count += 1

# Output results
output_path = "scan_output/gpt_patch_suggestions.md"
if patch_suggestions:
    os.makedirs("scan_output", exist_ok=True)
    with open(output_path, "w") as f:
        f.write("# GPT-Generated Patch Suggestions\n\n")
        f.write("\n---\n\n".join(patch_suggestions))
    print(f"\n✅ Patch suggestions written to {output_path} for {processed_count} vulnerabilities.")
else:
    print("\n⚠️ No patch suggestions generated. Please check Trivy report content or severity filter.")

print(f"\n📊 Summary:\n- Processed: {processed_count}\n- Skipped: {skipped_count}")
