"""
This module is responsible for storing the state of the response
"""

from typing import Optional


class Response:
    def __init__(
            self,
            status_code: Optional[int] = None,
            body: Optional[str] = None
    ):
        self.status_code: Optional[int] = status_code
        self.body: Optional[str] = body
