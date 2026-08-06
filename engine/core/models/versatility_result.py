"""
ScoutVision Core
Versatility Result Model
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VersatilityResult:

    score: int

    range: float

    dominance: float

    balanced: bool
