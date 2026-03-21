import requests

from features.src.commons.context.http import Http
from features.src.commons.services.json.converts_json_to_str import ConvertsJsonToStr
from features.src.commons.services.json.converts_str_to_json import ConvertsStrToJson


class DoHttpRequest:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(DoHttpRequest, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, http: Http) -> None:
        headers = http.request.headers or {}
        params = http.request.params or {}
        body = self._get_request_body(http)
        method = http.request.method.upper()
        url = http.request.url

        response = requests.request(
            method, url,
            headers=headers,
            params=params,
            data=body if method in ("POST", "PUT", "PATCH") else None,
            timeout=http.request.timeout
        )

        http.response.body = response.content.decode("utf-8") if response.content else None
        http.response.status_code = response.status_code

    def _get_request_body(self, http: Http):
        if http.request.body is None:
            return None
        body = http.request.body
        if isinstance(body, str):
            json_body = ConvertsStrToJson().execute(body)
            if json_body:
                return ConvertsJsonToStr().execute(json_body)
        return body
