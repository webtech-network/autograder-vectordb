import json
from typing import Any


class ConvertsStrToJson:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(ConvertsStrToJson, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, content: str) -> Any:
        if not content:
            return None
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return None
