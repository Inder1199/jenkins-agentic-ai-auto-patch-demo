import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to the vulnerable app!"

@app.route("/ping", methods=["GET"])
def ping():
    host = request.args.get("host", "127.0.0.1")
    # ⚠️ Vulnerable to Command Injection
    result = subprocess.getoutput(f"ping -c 1 {host}")
    return f"<pre>{result}</pre>"

@app.route("/secret")
def secret():
    # ⚠️ Simulates exposure of sensitive info
    return f"API_KEY={os.getenv('SECRET_API_KEY', 'not_set')}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
