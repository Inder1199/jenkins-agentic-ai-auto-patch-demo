import json
import os
import sys
import subprocess

OLLAMA_MODEL = "llama3"
TRIVY_REPORT = "scan_output/trivy_report.json"
OUTPUT_FILE = "scan_output/gpt_patch_suggestions.md"

# Check if Trivy scan report exists
if not os.path.exists(TRIVY_REPORT):
    print("❌ Trivy report not found at scan_output/trivy_report.json")
    sys.exit(1)

# Load Trivy report
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

# Use Ollama CLI to get suggestion from llama3
def get_ollama_suggestion(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60
        )
        if result.returncode != 0:
            print(f"⚠️ Ollama failed: {result.stderr.decode().strip()}")
            return None
        return result.stdout.decode().strip()
    except subprocess.TimeoutExpired:
        print("⚠️ Ollama inference timed out.")
        return None

# Process and generate patch suggestions
for target_name, vuln in critical_vulns:
    vuln_id = vuln.get("VulnerabilityID")
    pkg = vuln.get("PkgName")
    installed = vuln.get("InstalledVersion")
    fixed = vuln.get("FixedVersion")
    severity = vuln.get("Severity")
    description = vuln.get("Description", "No description available.")

    print(f"\n📦 Processing: {vuln_id} in {pkg} ({severity})")

    prompt = (
        f"You are a DevSecOps AI assistant.\n\n"
        f"Vulnerability ID: {vuln_id}\n"
        f"Package: {pkg}\n"
        f"Installed Version: {installed}\n"
        f"Fixed Version: {fixed}\n"
        f"Severity: {severity}\n"
        f"Description: {description}\n\n"
        "Suggest a patch or mitigation for this vulnerability. "
        "Return the answer in Markdown format."
    )

    suggestion = get_ollama_suggestion(prompt)
    if suggestion:
        patch_suggestions.append(f"## {vuln_id} ({severity}) in `{pkg}`\n\n{suggestion}\n")
    else:
        print(f"⚠️ Skipped {vuln_id} due to Ollama failure.")

# Write results to markdown
if patch_suggestions:
    os.makedirs("scan_output", exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write("# Ollama LLM Patch Suggestions (PoC)\n\n")
        f.write("\n---\n\n".join(patch_suggestions))
    print(f"\n✅ Patch suggestions written to `{OUTPUT_FILE}`")
else:
    print("\n⚠️ No suggestions generated.")
