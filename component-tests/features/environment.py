import logging

from features.src.business.context.global_context import GlobalContext
from features.src.business.context.scenario_context import ScenarioContext
from features.src.commons.services.docker.start_docker_compose import StartDockerCompose
from features.src.commons.services.docker.stop_docker_compose import StopDockerCompose


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

_LOGGER = logging.getLogger(__name__)


def before_all(context):
    _LOGGER.info('=== Starting component-tests ===')
    global_context = GlobalContext()
    context.global_context = global_context

    global_context.docker_compose = StartDockerCompose().execute(
        docker_compose_yml_file="docker/docker-compose.yml",
        logs_to_verify_by_service_name={
            "tests-autograder-vectordb-api": "Application startup complete."
        }
    )


def after_all(context):
    global_context: GlobalContext = context.global_context
    StopDockerCompose().execute(global_context.docker_compose)
    _LOGGER.info('=== Ending component-tests ===')


def before_scenario(context, scenario):
    _LOGGER.info(f'=== Starting scenario: {scenario.name} ===')
    scenario_context = ScenarioContext()
    context.scenario_context = scenario_context


def after_scenario(context, scenario):
    _LOGGER.info(f'=== Ending scenario: {scenario.name} ===')
    del context.scenario_context
