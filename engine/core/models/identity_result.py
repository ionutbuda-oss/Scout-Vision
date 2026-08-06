"""
ScoutVision Core
Identity Result Model
"""

from dataclasses import dataclass

from engine.core.models.identity_score import IdentityScore


@dataclass(frozen=True)
class IdentityResult:

    winner: IdentityScore

    runner_up: IdentityScore | None

    difference: float

    ranking: list[IdentityScore]
