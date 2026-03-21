import json
from typing import Any


class ConvertsJsonToStr:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(ConvertsJsonToStr, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, content: Any) -> str:
        if not content:
            return None
        try:
            return json.dumps(content, indent=2, sort_keys=True, ensure_ascii=False)
        except Exception:
            return None
