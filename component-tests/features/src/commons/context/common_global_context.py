"""
Stores data used between all scenarios.
"""

from typing import Optional
from testcontainers.compose import DockerCompose


class CommonGlobalContext:
    def __init__(
            self,
            docker_compose: Optional[DockerCompose] = None
    ):
        self.docker_compose: Optional[DockerCompose] = docker_compose
