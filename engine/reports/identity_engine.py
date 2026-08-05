"""
ScoutVision Identity Engine
"""

from __future__ import annotations


AM_PROFILES = [
    {
        "profile": "Creative Playmaker",
        "primary": "Creativity",
        "secondary": "Progression",
    },
    {
        "profile": "Advanced Creator",
        "primary": "Creativity",
        "secondary": "Goal Threat",
    },
    {
        "profile": "Progressive Playmaker",
        "primary": "Progression",
        "secondary": "Creativity",
    },
    {
        "profile": "Dynamic Attacking Midfielder",
        "primary": "Ball Carrying",
        "secondary": "Goal Threat",
    },
]


def build_am_profile(scores: dict[str, float]) -> str:
    ordered = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    primary = ordered[0][0]
    secondary = ordered[1][0]

    for profile in AM_PROFILES:
        if (
            profile["primary"] == primary
            and profile["secondary"] == secondary
        ):
            return {
                "profile": profile["profile"],
                "archetype": profile["profile"].split()[0],
                "confidence": 100,
                "primary": primary,
                "secondary": secondary,
            }

    return {
        "profile": "Hybrid Attacking Midfielder",
        "archetype": "Hybrid",
        "confidence": 50,
        "primary": primary,
        "secondary": secondary,
    }
