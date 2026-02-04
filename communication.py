from dataclasses import dataclass, field
from typing import Any
import requests
from requests import codes

@dataclass
class Response:
    """
    Dataclass to encapsulate an HTTP response with a status code and data payload.
    """
    # Default to internal server error since valid code paths must set this - safer as it will highlight unhandled cases. (could also shoot myself in the foot)
    status_code: int = codes.internal_server_error
    data: dict[str, Any] | list[Any] = field(default_factory=dict)

    def to_tuple(self) -> tuple[dict[str, Any] | list[Any], int]:
        return self.data, self.status_code
    

def make_request(url: str, method: str, response: Response, json_payload: dict[str, str] = None, headers: dict[str, str] = None) -> tuple[dict[str, str] | list[Any], bool]:
    """
    Helper function to make requests and handle errors.
    
    :param url: URL of the endpoint to send the request to
    :type url: str
    :param json_payload: JSON payload to send in the request
    :type json_payload: dict[str, str]
    :param response: Response object to set status code on (note: this is the response from auberge)
    :type response: Response
    :return: Tuple containing the JSON response from the endpoint and a boolean indicating success
    :rtype: tuple[dict[str, str] | list[Any], bool]
    """
    try:
        rsp = requests.request(method, url, json=json_payload, headers=headers)
    except requests.RequestException:
        response.status_code = codes.internal_server_error
        return {}, False
    
    if rsp.status_code != codes.ok:
        response.status_code = codes.bad_gateway
        return {}, False
    
    rsp_json = rsp.json()
    if rsp_json is None:
        response.status_code = codes.internal_server_error
        return {}, False
    
    return rsp_json, True