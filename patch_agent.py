import os
import json
import sys
from openai import OpenAI
from openai.types.chat import ChatCompletion

# Load API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Load Trivy scan results
trivy_report_path = "scan_output/trivy_report.json"
if not os.path.exists(trivy_report_path):
    print(f"❌ Trivy report not found at: {trivy_report_path}")
    sys.exit(1)

with open(trivy_report_path, "r") as f:
    try:
        data = json.load(f)
    except json.JSONDecodeError:
        print("❌ Failed to parse trivy_report.json (invalid JSON)")
        sys.exit(1)

results = data.get("Results", [])
if not results:
    print("✅ No vulnerabilities found in Trivy report.")
    sys.exit(0)

# Loop through vulnerabilities and get GPT patch suggestions
for target in results:
    target_name = target.get("Target", "Unknown Target")
    vulns = target.get("Vulnerabilities", [])