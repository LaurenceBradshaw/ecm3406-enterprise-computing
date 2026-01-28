import requests
from requests.status_codes import codes
from flask import Flask, request, jsonify
import re

# If for whatever reason the guardrails or llm modules cannot be imported
try:
    from guardrails import GUARDRAILS_PORT
except ImportError:
    GUARDRAILS_PORT = 3001
try:
    from llm import LLM_PORT
except ImportError:
    LLM_PORT = 3000

AUBERGE_PORT = 3002
GUARDRAILS_URL = f"http://localhost:{GUARDRAILS_PORT}/guardrails"
LLM_URL = f"http://localhost:{LLM_PORT}/llm"

app = Flask(__name__)

@app.route("/auberge", methods=["POST"])
def auberge():
    request_json = request.get_json()
    prompt = request_json.get("prompt")
    if not(prompt and type(prompt) == str):
        return {}, codes.bad_request
    
    # Get guardrail IDs
    rsp = requests.get(GUARDRAILS_URL)
    if rsp.status_code != codes.ok:
        return {}, codes.internal_server_error
    
    guardrail_ids = rsp.json()
    guardrails = []
    for gid in guardrail_ids:
        rsp = requests.get(f"{GUARDRAILS_URL}/{gid}")
        if rsp.status_code != codes.ok:
            return {}, codes.internal_server_error
        
        guardrail = rsp.json()
        guardrails.append(guardrail)

    # Apply guardrails to prompt
    modified_prompt = prompt
    for gr in guardrails:
        try:
            pattern = re.compile(gr["regx"])
            modified_prompt = pattern.sub(gr["sub"], modified_prompt)
        except re.error:
            return {}, codes.internal_server_error

    # Send modified prompt to LLM
    rsp = requests.post(LLM_URL, json={"prompt": modified_prompt})
    if rsp.status_code != codes.ok:
        return {}, codes.internal_server_error
    
    # Apply guardrails to LLM output
    output = rsp.json().get("output")
    for gr in guardrails:
        try:
            pattern = re.compile(gr["regx"])
            output = pattern.sub(gr["sub"], output)
        except re.error:
            return {}, codes.internal_server_error
    
    return jsonify(output=output), codes.ok

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=AUBERGE_PORT)