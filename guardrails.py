from typing import Any
import database
from flask import Flask, request
import re
from requests.status_codes import codes
from response import Response

def handle_repository_error(result: None | bool, response: Response) -> bool:
    """
    Helper function to handle repository errors and set appropriate response status codes.
    
    :param result: Result from a repository operation
    :type result: None | bool
    :param response: Response object to set status code on
    :type response: Response
    :return: True if an error was handled, otherwise False
    :rtype: bool
    """
    if result is None:
        response.status_code = codes.internal_server_error
        return True
    if result is False:
        response.status_code = codes.bad_gateway
        return True
    return False


GUARDRAILS_PORT = 3001

app = Flask(__name__)

@app.route("/guardrails/<string:id>", methods=["PUT"])
def create_guardrail(id: str) -> tuple[dict[str, Any], int]:
    """
    Create or update a guardrail with the given ID.

    Expects a JSON body with "id", "regx", and "sub" fields.
    
    :param id: Guardrail ID
    :type id: str
    :return: Response tuple with status code
    :rtype: tuple[dict[str, Any], int]
    """
    res = Response()
    request_json = request.get_json()
    if request_json is None:
        res.status_code = codes.bad_request
        return res.to_tuple()
    
    id2 = request_json.get("id")
    regx = request_json.get("regx")
    sub = request_json.get("sub")
    if not(type(id2) == str and type(regx) == str and type(sub) == str and id == id2):
        res.status_code = codes.bad_request
        return res.to_tuple()
    
    # Validate regex
    try:
        re.compile(regx)
    except re.error:
        res.status_code = codes.bad_request
        return res.to_tuple()
    
    js = {"id": id2, "regx": regx, "sub": sub}
    lookup = database.db.lookup(id)
    err = handle_repository_error(lookup, res)
    if err:
        return res.to_tuple()
    
    if lookup == {}:
        insert = database.db.insert(js)
        err = handle_repository_error(insert, res)
        if err:
            return res.to_tuple()
        
        res.status_code = codes.created
    else:
        update = database.db.update(js)
        err = handle_repository_error(update, res)
        if err:
            return res.to_tuple()
        
        res.status_code = codes.no_content

    return res.to_tuple()
            
@app.route("/guardrails/<string:id>", methods=["GET"])
def get_guardrail(id: str) -> tuple[dict[str, Any], int]:
    """
    Retrieve a guardrail by its ID.
    
    :param id: Guardrail ID to retrieve
    :type id: str
    :return: Response tuple with guardrail data or status code
    :rtype: tuple[dict[str, Any], int]
    """
    res = Response()
    
    lookup = database.db.lookup(id)
    err = handle_repository_error(lookup, res)
    if err:
        return res.to_tuple()
    
    if lookup == {}:
        res.status_code = codes.not_found
    else:
        res.data = lookup
        res.status_code = codes.ok
    
    return res.to_tuple()
    
@app.route("/guardrails/<string:id>", methods=["DELETE"])
def delete_guardrail(id: str) -> tuple[dict[str, Any], int]:
    """
    Delete a guardrail by its ID.
    
    :param id: Guardrail ID to delete
    :type id: str
    :return: Response tuple with status code
    :rtype: tuple[dict[str, Any], int]
    """
    res = Response()
    
    lookup = database.db.lookup(id)
    err = handle_repository_error(lookup, res)
    if err:
        return res.to_tuple()
    
    if lookup == {}:
        res.status_code = codes.not_found
        return res.to_tuple()
    
    delete = database.db.delete(id)
    err = handle_repository_error(delete, res)
    if err:
        return res.to_tuple()
    
    res.status_code = codes.no_content
    return res.to_tuple()
    
@app.route("/guardrails", methods=["GET"])
def list_guardrails() -> tuple[list[Any], int]:
    """
    List all guardrail IDs.

    :return: Response tuple with list of guardrail IDs
    :rtype: tuple[list[Any], int]
    """
    res = Response()
    ids = database.db.get_ids()
    err = handle_repository_error(ids, res)
    if err:
        return res.to_tuple()
    
    res.data = ids
    res.status_code = codes.ok
    return res.to_tuple()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=GUARDRAILS_PORT)
