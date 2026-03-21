"""
Stores data used between steps of a scenario
"""

from typing import Optional

from features.src.commons.context.request import Request
from features.src.commons.context.response import Response


class Http:
    def __init__(
            self,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ):
        self.request: Request = request if request is not None else Request()
        self.response: Response = response if response is not None else Response()
