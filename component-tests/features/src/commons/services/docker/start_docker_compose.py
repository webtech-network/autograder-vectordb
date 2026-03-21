import os
import time
import logging
import subprocess
from typing import Dict
from testcontainers.compose import DockerCompose


class StartDockerCompose:

    _INSTANCE = None
    _LOGGER = logging.getLogger(__name__)

    def __new__(cls):
        if cls._INSTANCE is None:
            cls._INSTANCE = super(StartDockerCompose, cls).__new__(cls)
        return cls._INSTANCE

    def execute(self, docker_compose_yml_file: str, logs_to_verify_by_service_name: Dict[str, str]) -> DockerCompose:
        if not os.path.exists(docker_compose_yml_file):
            raise Exception(f"Docker compose file not found: {docker_compose_yml_file}")

        self._LOGGER.info("Starting docker compose")
        docker_compose = self._start_docker_compose(docker_compose_yml_file)
        for service_name, expected_log in logs_to_verify_by_service_name.items():
            self._verify_log_in_service(service_name, expected_log, docker_compose_yml_file)

        self._LOGGER.info("Docker compose started")
        return docker_compose

    def _start_docker_compose(self, docker_compose_yml_file: str) -> DockerCompose:
        os.environ['COMPOSE_HTTP_TIMEOUT'] = "300"
        docker_compose = DockerCompose(
            filepath=os.path.dirname(docker_compose_yml_file),
            compose_file_name=os.path.basename(docker_compose_yml_file)
        )

        last_error = None
        for _ in range(6):
            try:
                docker_compose.start()
                return docker_compose
            except Exception as e:
                last_error = e
                self._LOGGER.warning(f"Error starting docker compose: {e}")
                time.sleep(10)

        raise last_error

    def _verify_log_in_service(self, service_name: str, expected_log: str, docker_compose_yml_file: str):
        self._LOGGER.info(f"Verifying log in service {service_name}")

        for _ in range(18):
            stdout, stderr, exit_code = self._get_log_from_service(service_name, docker_compose_yml_file)
            if exit_code == 0 and expected_log in stdout:
                self._LOGGER.info(f"Log found in service {service_name}")
                return
            self._LOGGER.info("Retrying in 10 seconds...")
            time.sleep(10)

        raise Exception(f"Log not found in service {service_name}: '{expected_log}'")

    def _get_log_from_service(self, service_name: str, docker_compose_yml_file: str):
        result = subprocess.run(
            ["docker", "compose", "logs", service_name],
            capture_output=True, check=False, text=True,
            cwd=os.path.dirname(docker_compose_yml_file)
        )
        return result.stdout, result.stderr, result.returncode
