"""
This module is responsible for storing the state of the request
"""

from typing import Optional


class Request:
    def __init__(
            self,
            method: Optional[str] = None,
            url: Optional[str] = None,
            headers: Optional[dict] = None,
            params: Optional[dict] = None,
            body: Optional[str] = None,
            timeout: Optional[int] = None
    ):
        self.method: Optional[str] = method
        self.url: Optional[str] = url
        self.headers: Optional[dict] = headers
        self.params: Optional[dict] = params
        self.body: Optional[str] = body
        self.timeout: Optional[int] = timeout
