import json
import os
import sys
import time
from openai import OpenAI

# Environment variables
OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    print("❌ OPENAI_API_KEY is not set.")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_KEY)

PRIMARY_MODEL = "gpt-4"
FALLBACK_MODEL = "gpt-3.5-turbo"

# Load Trivy scan results
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

patch_suggestions = []
processed_count = 0
skipped_count = 0


def get_patch_suggestion(prompt: str, model: str) -> str:
    """Fetch patch suggestion from GPT model with retries."""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a security DevOps assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Attempt {attempt + 1} with {model} failed: {e}")
            if "insufficient_quota" in str(e) or "rate_limit" in str(e):
                time.sleep(2 ** attempt)  # backoff
            else:
                break
    return None


for idx, target in enumerate(results):
    target_name = target.get("Target", "unknown")
    vulns = target.get("Vulnerabilities", [])

    if not vulns:
        print(f"⏭️ No vulnerabilities in: {target_name}")
        continue

    print(f"\n📦 Target {idx + 1}: {target_name} — {len(vulns)} vulnerabilities")

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

        suggestion = get_patch_suggestion(prompt, PRIMARY_MODEL)
        if not suggestion:
            suggestion = get_patch_suggestion(prompt, FALLBACK_MODEL)

        if suggestion:
            patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
            processed_count += 1
        else:
            print(f"⚠️ Skipped {vuln_id} due to repeated failures.")
            skipped_count += 1

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
