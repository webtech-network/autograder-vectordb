from behave import when

from features.src.business.config.endpoint_enum import EndpointEnum
from features.src.business.context.scenario_context import ScenarioContext


@when(u'I send a GET request to Healthcheck endpoint')
def i_send_a_get_request_to_healthcheck(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "GET"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_HEALTHCHECK_ENDPOINT.value


@when(u'I send a POST request to Create Index endpoint')
def i_send_a_post_request_to_create_index(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_CREATE_INDEX_ENDPOINT.value


@when(u'I send a GET request to List Indexes endpoint')
def i_send_a_get_request_to_list_indexes(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "GET"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_LIST_INDEXES_ENDPOINT.value


@when(u'I send a GET request to Get Index endpoint with index "{index_name}"')
def i_send_a_get_request_to_get_index(context, index_name):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "GET"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_GET_INDEX_TEMPLATE.value.format(index_name=index_name)


@when(u'I send a DELETE request to Delete Index endpoint with index "{index_name}"')
def i_send_a_delete_request_to_delete_index(context, index_name):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "DELETE"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_DELETE_INDEX_TEMPLATE.value.format(index_name=index_name)


@when(u'I send a POST request to Ingest Text endpoint')
def i_send_a_post_request_to_ingest_text(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_INGEST_TEXT_ENDPOINT.value


@when(u'I send a POST request to Ingest Vectors endpoint')
def i_send_a_post_request_to_ingest_vectors(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_INGEST_VECTORS_ENDPOINT.value


@when(u'I send a POST request to Upsert Vectors endpoint with index "{index_name}"')
def i_send_a_post_request_to_upsert_vectors(context, index_name):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_UPSERT_VECTORS_TEMPLATE.value.format(index_name=index_name)


@when(u'I send a POST request to Query endpoint')
def i_send_a_post_request_to_query(context):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_QUERY_ENDPOINT.value


@when(u'I send a POST request to Query Index endpoint with index "{index_name}"')
def i_send_a_post_request_to_query_index(context, index_name):
    scenario_context: ScenarioContext = context.scenario_context
    scenario_context.http.request.method = "POST"
    scenario_context.http.request.url = EndpointEnum.LOCAL_API_QUERY_INDEX_TEMPLATE.value.format(index_name=index_name)
