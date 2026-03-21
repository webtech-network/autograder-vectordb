"""
Stores data used between all scenarios.
"""

from typing import Optional
from testcontainers.compose import DockerCompose

from features.src.commons.context.common_global_context import CommonGlobalContext


class GlobalContext(CommonGlobalContext):
    def __init__(self, docker_compose: Optional[DockerCompose] = None):
        super().__init__(docker_compose=docker_compose)
