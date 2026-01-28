import os
import requests
from requests.status_codes import codes
from flask import Flask, request

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"
LLM_PORT = 3000

app = Flask(__name__)

@app.route("/llm", methods=["POST"])
def llm():
    request_json = request.get_json()
    prompt = request_json.get("prompt")
    if not(prompt and type(prompt) == str):
        return {}, codes.bad_request

    # Since the mistralai package is not installed in the environment in Lovelace
    # need to manually craft the HTTP request.
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        response = requests.post(
            MISTRAL_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code != codes.ok:
            return {}, codes.internal_server_error
        
        response_json = response.json()
        output_text = response_json["choices"][0]["message"]["content"]

        return {"output": output_text}, codes.ok

    except requests.RequestException as exc:
        return {}, codes.internal_server_error

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=LLM_PORT)