"""
ScoutVision Core
Decision Trace Model
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DecisionStep:

    engine: str

    output: dict[str, Any]


@dataclass
class DecisionTrace:

    steps: list[DecisionStep] = field(default_factory=list)

    def add_step(self, engine: str, output: dict[str, Any]) -> None:
        self.steps.append(
            DecisionStep(
                engine=engine,
                output=output
            )
        )
