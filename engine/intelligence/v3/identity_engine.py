"""
ScoutVision DNA Engine v3
Identity Engine

Responsibility:
- Evaluate specialist profiles
- Rank profile scores
- Return the specialist ranking
"""

from typing import Dict, List
from engine.core.models.identity_definition import IdentityDefinition
from engine.core.models.identity_score import IdentityScore
from engine.core.models.identity_result import IdentityResult


def choose_specialist_identity(
    competencies: Dict[str, float],
    profiles: List[dict],
):
    """
    Evaluate all specialist profiles and return the full ranking.
    """

    scored_profiles = []

    for profile in profiles:

        score = 0.0

        for metric, weight in profile["weights"].items():
            score += competencies.get(metric, 0) * weight

        scored_profiles.append({
            "profile": profile,
            "score": round(score, 1),
        })

    scored_profiles.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    winner = scored_profiles[0]

    runner_up = (
        scored_profiles[1]
        if len(scored_profiles) > 1
        else None
    )

    difference = (
        round(
            winner["score"] - runner_up["score"],
            1,
        )
        if runner_up
        else winner["score"]
    )

    return {
        "winner": winner,
        "runner_up": runner_up,
        "difference": difference,
        "ranking": scored_profiles,
 }
