import logging
from testcontainers.compose import DockerCompose


class StopDockerCompose:

    _INSTANCE = None
    _LOGGER = logging.getLogger(__name__)

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(StopDockerCompose, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, docker_compose: DockerCompose) -> None:
        if docker_compose is None:
            raise Exception("Docker compose is None")

        self._LOGGER.info("Stopping docker compose")
        docker_compose.stop()
        self._LOGGER.info("Docker compose stopped")
