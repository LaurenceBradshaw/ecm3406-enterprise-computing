from dataclasses import dataclass, field
from typing import Any
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