from typing import Any

from features.src.commons.services.json.converts_json_to_str import ConvertsJsonToStr


class AssertThatTheJsonsAreEquals:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(AssertThatTheJsonsAreEquals, cls).__new__(cls)
        return cls._INSTANCE

    def _find_differences(self, actual, expected, path=""):
        differences = []

        if type(actual) != type(expected):
            differences.append(f"{path}: type mismatch - actual: {type(actual).__name__}, expected: {type(expected).__name__}")
            return differences

        if isinstance(actual, dict):
            all_keys = set(actual.keys()) | set(expected.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key not in actual:
                    differences.append(f"{new_path}: missing in actual")
                elif key not in expected:
                    differences.append(f"{new_path}: extra in actual")
                else:
                    differences.extend(self._find_differences(actual[key], expected[key], new_path))
        elif isinstance(actual, list):
            if len(actual) != len(expected):
                differences.append(f"{path}: length mismatch - actual: {len(actual)}, expected: {len(expected)}")
            for i in range(min(len(actual), len(expected))):
                differences.extend(self._find_differences(actual[i], expected[i], f"{path}[{i}]"))
        else:
            if actual != expected:
                differences.append(f"{path}: value mismatch - actual: {actual}, expected: {expected}")

        return differences

    def execute(self, expected_json: Any, actual_json: Any, error_message_prefix: str):
        differences = self._find_differences(actual_json, expected_json)
        converts_json_to_str_service = ConvertsJsonToStr()

        if differences:
            diff_summary = "\n".join(differences[:10])
            if len(differences) > 10:
                diff_summary += f"\n... and {len(differences) - 10} more differences"

            assert False, (
                f"{error_message_prefix}"
                f"\nActual  : {converts_json_to_str_service.execute(actual_json)}"
                f"\nExpected: {converts_json_to_str_service.execute(expected_json)}"
                f"\nDiff    : {diff_summary}"
            )
