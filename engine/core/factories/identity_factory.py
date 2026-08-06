"""
ScoutVision Core
Identity Factory

Responsible for building IdentityResult objects.
"""

from engine.core.models.identity_profile import IdentityProfile
from engine.core.models.identity_result import IdentityResult


def build_identity_result(
    winner_profile: dict,
    winner_score: float,
    runner_up_profile: dict,
    runner_up_score: float,
) -> IdentityResult:

    winner = IdentityProfile(
        key=winner_profile["key"],
        title=winner_profile["title"],
        signature=winner_profile["signature"],
        archetype=winner_profile["archetype"],
        description=winner_profile["description"],
        executive_summary=winner_profile["executive_summary"],
        weights=winner_profile["weights"],
        score=winner_score,
    )

    runner_up = IdentityProfile(
        key=runner_up_profile["key"],
        title=runner_up_profile["title"],
        signature=runner_up_profile["signature"],
        archetype=runner_up_profile["archetype"],
        description=runner_up_profile["description"],
        executive_summary=runner_up_profile["executive_summary"],
        weights=runner_up_profile["weights"],
        score=runner_up_score,
    )

    return IdentityResult(
        winner=winner,
        runner_up=runner_up,
        difference=round(winner_score - runner_up_score, 1),
    )
