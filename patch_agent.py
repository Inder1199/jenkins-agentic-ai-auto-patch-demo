import json, openai

openai.api_key = "sk-..."  # Replace with your OpenAI key

def generate_patch(vuln_desc):
    prompt = f"Fix the following Python vulnerability: {vuln_desc}"
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

with open("trivy_report.json") as f:
    data = json.load(f)

for result in data.get("Results", []):
    for vuln in result.get("Vulnerabilities", []):
        suggestion = generate_patch(vuln['Description'])
        print("Patch Suggestion:\n", suggestion)
        with open("patch_suggestion.txt", "a") as pf:
            pf.write(suggestion + "\n\n")
