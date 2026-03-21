"""
Stores data used between steps of a scenario.
"""

from typing import Optional

from features.src.commons.context.common_scenario_context import CommonScenarioContext
from features.src.commons.context.http import Http


class ScenarioContext(CommonScenarioContext):
    def __init__(self, http: Optional[Http] = None):
        super().__init__(http=http)
