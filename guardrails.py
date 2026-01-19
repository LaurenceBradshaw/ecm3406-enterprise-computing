import os
import requests
import database
from flask import Flask, request
import re

GUARDRAILS_PORT = 3001

app = Flask(__name__)

@app.route("/guardrails/<string:id>", methods=["POST", "PUT"])
def create_guardrail(id):
    request_json = request.get_json()
    id2 = request_json.get("id")
    regx = request_json.get("regx")
    sub = request_json.get("sub")
    if not(type(id2) == str and type(regx) == str and type(sub) == str and id == id2):
        return {}, 400 # Bad Request
    
    # Validate regex
    try:
        re.compile(regx)
    except re.error:
        return {}, 400 # Bad Request
    
    js = {"id": id2, "regx": regx, "sub": sub}
    if database.db.lookup(id):
        if database.db.update(js):
            return {}, 204 # No Content
        else:
            return {}, 500 # Internal Server Error
    else:
        if database.db.insert(js):
            return {}, 201 # Created
        else:
            return {}, 500 # Internal Server Error
            
@app.route("/guardrails/<string:id>", methods=["GET"])
def get_guardrail(id):
    record = database.db.lookup(id)
    if record:
        return record, 200 # OK
    else:
        return {}, 404 # Not Found
    
@app.route("/guardrails/<string:id>", methods=["DELETE"])
def delete_guardrail(id):
    if database.db.delete(id):
        return {}, 204 # No Content
    else:
        return {}, 500 # Internal Server Error
    
@app.route("/guardrails", methods=["GET"])
def list_guardrails():
    try:
        ids = database.db.get_ids()
        return ids, 200 # OK
    except Exception as exc:
        return {}, 500 # Internal Server Error

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=GUARDRAILS_PORT)
