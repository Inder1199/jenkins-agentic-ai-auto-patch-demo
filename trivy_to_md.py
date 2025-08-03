import json

with open("trivy_report.json") as f:
    data = json.load(f)

with open("reports/trivy_report.md", "w") as out:
    out.write("# Trivy Vulnerability Report\n\n")
    for result in data.get("Results", []):
        out.write(f"## Target: {result['Target']}\n")
        for vuln in result.get("Vulnerabilities", []):
            out.write(f"- **ID**: {vuln['VulnerabilityID']}\n")
            out.write(f"  - Package: `{vuln['PkgName']}@{vuln['InstalledVersion']}`\n")
            out.write(f"  - Description: {vuln['Description']}\n\n")
