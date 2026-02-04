from requests.status_codes import codes
from flask import Flask, request
import re
from communication import Response, make_request

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
def auberge() -> tuple[dict[str, str], int]:
    """
    Process a prompt by applying guardrails and then sending it to the 
    LLM service then applying guardrails to the output.
    
    :return: Response tuple with LLM output after applying guardrails
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
    
    # Get guardrail IDs
    gid_list, success = make_request(GUARDRAILS_URL, "GET", res)
    if not success:
        return res.to_tuple()
    
    # Fetch guardrails by ID
    guardrails = []
    for gid in gid_list:
        guardrail, success = make_request(f"{GUARDRAILS_URL}/{gid}", "GET", res)
        if not success:
            return res.to_tuple()
        guardrails.append(guardrail)

    # Apply guardrails to prompt
    modified_prompt = prompt
    for gr in guardrails:
        try:
            pattern = re.compile(gr["regx"])
            modified_prompt = pattern.sub(gr["sub"], modified_prompt)
        except re.error:
            # Shouldn't happen since the regex was validated when the guardrail was created, but just in case
            res.status_code = codes.internal_server_error
            return res.to_tuple()

    # Send modified prompt to LLM microservice
    llm_rsp_json, success = make_request(LLM_URL, "POST", res, {"prompt": modified_prompt})
    if not success:
        return res.to_tuple()
    
    # Apply guardrails to LLM output
    output = llm_rsp_json.get("output")
    for gr in guardrails:
        try:
            pattern = re.compile(gr["regx"])
            output = pattern.sub(gr["sub"], output)
        except re.error:
            # Shouldn't happen since the regex was validated when the guardrail was created, but just in case
            res.status_code = codes.internal_server_error
            return res.to_tuple()
    
    # Return final output
    res.data = {"output": output}
    res.status_code = codes.ok
    return res.to_tuple()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=AUBERGE_PORT)