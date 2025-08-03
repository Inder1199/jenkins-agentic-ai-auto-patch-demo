import json
import sys
import os

def convert_to_html(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)

    html = """<html><head><title>Trivy Vulnerability Report</title>
    <style>body{font-family:Arial}table{width:100%;border-collapse:collapse}
    th,td{border:1px solid #ccc;padding:8px;text-align:left}
    th{background:#eee}</style></head><body>
    <h1>Trivy Vulnerability Report</h1>"""

    for result in data.get("Results", []):
        html += f"<h2>{result.get('Target')} ({result.get('Type')})</h2>"
        vulns = result.get("Vulnerabilities", [])
        if not vulns:
            html += "<p><i>No vulnerabilities found.</i></p>"
            continue
        html += "<table><tr><th>ID</th><th>Severity</th><th>Pkg</th><th>Installed</th><th>Fixed</th><th>Refs</th></tr>"
        for v in vulns:
            refs = ', '.join(v.get("References", [])[:2])
            html += f"<tr><td>{v['VulnerabilityID']}</td><td>{v['Severity']}</td><td>{v['PkgName']}</td>"
            html += f"<td>{v['InstalledVersion']}</td><td>{v.get('FixedVersion', 'N/A')}</td><td>{refs}</td></tr>"
        html += "</table><br/>"
    html += "</body></html>"
    return html

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 trivy_to_html.py <trivy_report.json>")
        sys.exit(1)
    os.makedirs("reports", exist_ok=True)
    html_content = convert_to_html(sys.argv[1])
    with open("reports/trivy_report.html", "w") as f:
        f.write(html_content)
    print("Generated: reports/trivy_report.html")
