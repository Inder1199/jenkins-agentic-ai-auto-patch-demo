import json
import sys
import os

def convert(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    if not data or "Results" not in data:
        print("No vulnerabilities found or invalid JSON.")
        return ""

    md = "# Trivy Vulnerability Report\n\n"

    for result in data.get("Results", []):
        md += f"## {result.get('Target')} ({result.get('Type')})\n\n"
        vulns = result.get("Vulnerabilities", [])
        if not vulns:
            md += "_No vulnerabilities found._\n\n"
            continue
        for v in vulns:
            md += f"- **{v.get('VulnerabilityID')}**: {v.get('Title', '')}\n"
            md += f"  - Severity: **{v.get('Severity')}**\n"
            md += f"  - Package: `{v.get('PkgName')}`\n"
            md += f"  - Installed Version: `{v.get('InstalledVersion')}`\n"
            md += f"  - Fixed Version: `{v.get('FixedVersion', 'N/A')}`\n"
            md += f"  - References: {', '.join(v.get('References', [])[:2])}\n\n"
    return md

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 trivy_to_md.py <trivy_report.json>")
        sys.exit(1)
    json_file = sys.argv[1]
    markdown = convert(json_file)
    os.makedirs("reports", exist_ok=True)
    with open("reports/trivy_report.md", "w") as f:
        f.write(markdown)
    print("Generated: reports/trivy_report.md")
