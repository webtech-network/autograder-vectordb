from features.src.commons.context.response import Response
from features.src.commons.services.json.converts_str_to_json import ConvertsStrToJson
from features.src.commons.services.json.assert_that_the_jsons_are_equals import AssertThatTheJsonsAreEquals


class CheckIfTheHttpResponseMatchesWhatIsExpected:

    _INSTANCE = None

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(CheckIfTheHttpResponseMatchesWhatIsExpected, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, response: Response, expected_status_code: int, expected_response_body: str) -> None:
        actual_response_body = response.body

        assert response.status_code == expected_status_code, (
            f"Expected status {expected_status_code}, got {response.status_code}"
            f"\nBody: {actual_response_body}"
        )

        expected_json = ConvertsStrToJson().execute(expected_response_body)
        if expected_json:
            actual_json = ConvertsStrToJson().execute(actual_response_body)
            AssertThatTheJsonsAreEquals().execute(
                expected_json=expected_json,
                actual_json=actual_json,
                error_message_prefix="Response body does not match."
            )
        else:
            assert actual_response_body == expected_response_body, (
                f"Response body mismatch.\nActual: {actual_response_body}\nExpected: {expected_response_body}"
            )
