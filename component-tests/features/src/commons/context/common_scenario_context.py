"""
Stores common data used as context in tests.
"""

from datetime import datetime, timezone
from typing import Optional

from features.src.commons.context.http import Http


class CommonScenarioContext:
    def __init__(
            self,
            scenario_start_time: Optional[datetime] = None,
            http: Optional[Http] = None
    ):
        self.scenario_start_time: datetime = scenario_start_time if scenario_start_time is not None else datetime.now(timezone.utc)
        self.http: Http = http if http is not None else Http()
