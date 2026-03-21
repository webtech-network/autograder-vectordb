from behave import given, then

from features.src.commons.context.common_scenario_context import CommonScenarioContext
from features.src.commons.context.request import Request
from features.src.commons.services.http.do_http_request import DoHttpRequest
from features.src.commons.services.http.get_expected_http_response_body import GetExpectedHttpResponseBody
from features.src.commons.services.http.get_http_request_body import GetHttpRequestBody
from features.src.commons.services.http.check_if_the_http_response_matches_what_is_expected import CheckIfTheHttpResponseMatchesWhatIsExpected


@given(u'I have the header "{header_name}" with value "{header_value}"')
def i_have_the_header_with_value(context, header_name: str, header_value: str):
    scenario_context: CommonScenarioContext = context.scenario_context
    if scenario_context.http.request.headers is None:
        scenario_context.http.request.headers = {}
    scenario_context.http.request.headers[header_name] = header_value


@given(u'I have the request payload at file "{file_name}" at folder "{folder_name}"')
def i_have_the_request_payload_at_file_at_folder(context, file_name: str, folder_name: str):
    request_body = GetHttpRequestBody().execute(
        file_name=f"{file_name}.json",
        folder_name=folder_name
    )
    scenario_context: CommonScenarioContext = context.scenario_context
    scenario_context.http.request.body = request_body


@then(u'I check that the http response code is "{status_code}" and the body matches the json at file "{file_name}" at folder "{folder_name}"')
def the_http_response_code_is_and_the_body_matches(context, status_code: str, file_name: str, folder_name: str):
    status_code = int(status_code)
    scenario_context: CommonScenarioContext = context.scenario_context

    try:
        DoHttpRequest().execute(scenario_context.http)
        expected_response_body = GetExpectedHttpResponseBody().execute(
            file_name=f"{file_name}.json",
            folder_name=folder_name
        )
        CheckIfTheHttpResponseMatchesWhatIsExpected().execute(
            response=scenario_context.http.response,
            expected_status_code=status_code,
            expected_response_body=expected_response_body
        )
    finally:
        scenario_context.http.request = Request()


@then(u'I check that the http response code is "{status_code}" only')
def the_http_response_code_is_only(context, status_code: str):
    status_code = int(status_code)
    scenario_context: CommonScenarioContext = context.scenario_context

    try:
        DoHttpRequest().execute(scenario_context.http)
        actual = scenario_context.http.response.status_code
        assert actual == status_code, f"Expected status code {status_code}, got {actual}"
    finally:
        scenario_context.http.request = Request()
