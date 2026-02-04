import os
import requests
from requests.status_codes import codes
from flask import Flask, request
from response import Response

MISTRAL_API_KEY = os.environ["MISTRAL_API_KEY"]
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small-latest"
LLM_PORT = 3000

app = Flask(__name__)

@app.route("/llm", methods=["POST"])
def llm() -> tuple[dict[str, str], int]:
    """
    Process a prompt using the Mistral LLM.
    
    :return: Response tuple with LLM output
    :rtype: tuple[dict[str, str], int]
    """
    res = Response()
    # Get JSON body
    request_json = request.get_json()
    if request_json is None:
        res.status_code = codes.bad_request
        return res.to_tuple()
    
    # Validate fields
    prompt = request_json.get("prompt")
    if not(prompt and type(prompt) == str):
        res.status_code = codes.bad_request
        return res.to_tuple()

    # Send request to Mistral API
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
        mistral_rsp = requests.post(
            MISTRAL_API_URL,
            headers=headers,
            json=payload
        )
    except requests.RequestException as exc:
        res.status_code = codes.internal_server_error
        return res.to_tuple()

    if mistral_rsp.status_code != codes.ok:
        res.status_code = codes.bad_gateway
        return res.to_tuple()
    
    # Parse response
    response_json = mistral_rsp.json()
    if (response_json is None \
        or "choices" not in response_json \
        or len(response_json["choices"]) == 0 \
        or "message" not in response_json["choices"][0] \
        or "content" not in response_json["choices"][0]["message"]
        ):
        res.status_code = codes.internal_server_error # or bad_gateway?
        return res.to_tuple()
    
    output_text = response_json["choices"][0]["message"]["content"]
    # Return output
    res.data = {"output": output_text}
    res.status_code = codes.ok
    return res.to_tuple()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=LLM_PORT)