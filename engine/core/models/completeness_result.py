"""
ScoutVision Core
Completeness Result Model
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompletenessResult:
    level: float
    minimum: float
    range: float
    is_complete_candidate: bool
