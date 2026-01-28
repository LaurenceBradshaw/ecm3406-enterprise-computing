import database
from flask import Flask, request
import re
from requests.status_codes import codes

GUARDRAILS_PORT = 3001

app = Flask(__name__)

@app.route("/guardrails/<string:id>", methods=["PUT"])
def create_guardrail(id):
    request_json = request.get_json()
    id2 = request_json.get("id")
    regx = request_json.get("regx")
    sub = request_json.get("sub")
    if not(type(id2) == str and type(regx) == str and type(sub) == str and id == id2):
        return {}, codes.bad_request
    
    # Validate regex
    try:
        re.compile(regx)
    except re.error:
        return {}, codes.bad_request
    
    js = {"id": id2, "regx": regx, "sub": sub}
    _, status = database.db.lookup(id)
    if status == codes.not_found:
        return database.db.insert(js)
    elif status == codes.ok:
        return database.db.update(js)
    else:
        return {}, status
            
@app.route("/guardrails/<string:id>", methods=["GET"])
def get_guardrail(id):
    if type(id) != str:
        return {}, codes.bad_request
    
    return database.db.lookup(id)
    
@app.route("/guardrails/<string:id>", methods=["DELETE"])
def delete_guardrail(id):
    if type(id) != str:
        return {}, codes.bad_request
    
    _, status = database.db.lookup(id)
    if status != codes.ok:
        return {}, status
    
    _, status = database.db.delete(id)
    return {}, status
    
@app.route("/guardrails", methods=["GET"])
def list_guardrails():
    ids, status = database.db.get_ids()
    if status != codes.ok:
        return {}, status
    
    return ids, codes.ok

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=GUARDRAILS_PORT)
