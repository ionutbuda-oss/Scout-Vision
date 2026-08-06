"""
ScoutVision Core
Confidence Result Model
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceResult:

    level: str

    score: int
